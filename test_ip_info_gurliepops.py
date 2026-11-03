"""
Unit tests for ip_info_gurliepops.py
DEVASC Project Activity 3 - Social Coding (Option 2)
Team: Gurliepops

Run with:
    pytest test_ip_info_gurliepops.py -v

These tests mock the network layer (fetch_url / requests.get), so they run
instantly and do not depend on the real ipapi.co / ipwho.is / ipify APIs
or on rate limits.
"""

import ipaddress

import pytest
from unittest.mock import MagicMock

import ip_info_gurliepops as app


# ---------------------------------------------------------------------------
# lookup_ipapi (main provider)
# ---------------------------------------------------------------------------
def test_lookup_ipapi_success(monkeypatch):
    sample = {
        "ip": "8.8.8.8",
        "version": "IPv4",
        "city": "Mountain View",
        "region": "California",
        "country_code": "US",
        "org": "GOOGLE",
        "asn": "AS15169",
        "timezone": "America/Los_Angeles",
    }
    monkeypatch.setattr(app, "fetch_json", lambda url: sample)

    result = app.lookup_ipapi("8.8.8.8")

    assert result["ip"] == "8.8.8.8"
    assert result["version"] == "IPv4"
    assert result["city"] == "Mountain View"
    assert result["asn"] == "AS15169"
    assert result["timezone"] == "America/Los_Angeles"


def test_lookup_ipapi_error_raises(monkeypatch):
    sample = {"error": True, "reason": "Invalid IP address"}
    monkeypatch.setattr(app, "fetch_json", lambda url: sample)

    with pytest.raises(app.ApiError, match="Invalid IP address"):
        app.lookup_ipapi("not-an-ip")


# ---------------------------------------------------------------------------
# lookup_ipwhois (backup provider)
# ---------------------------------------------------------------------------
def test_lookup_ipwhois_success(monkeypatch):
    sample = {
        "success": True,
        "ip": "8.8.8.8",
        "type": "IPv4",
        "city": "Mountain View",
        "region": "California",
        "country_code": "US",
        "connection": {"org": "Google LLC", "isp": "Google LLC", "asn": 15169},
        "timezone": {"id": "America/Los_Angeles"},
    }
    monkeypatch.setattr(app, "fetch_json", lambda url: sample)

    result = app.lookup_ipwhois("8.8.8.8")

    assert result["ip"] == "8.8.8.8"
    assert result["org"] == "Google LLC"
    assert result["asn"] == "AS15169"
    assert result["timezone"] == "America/Los_Angeles"


def test_lookup_ipwhois_failure_raises(monkeypatch):
    sample = {"success": False, "message": "invalid IP address"}
    monkeypatch.setattr(app, "fetch_json", lambda url: sample)

    with pytest.raises(app.ApiError, match="invalid IP address"):
        app.lookup_ipwhois("not-an-ip")


# ---------------------------------------------------------------------------
# lookup_ip: falls back from the main provider to the backup provider
# ---------------------------------------------------------------------------
def test_lookup_ip_falls_back_to_second_provider(monkeypatch):
    def primary_fails(address=""):
        raise app.ApiError("ipapi.co is down")

    def backup_ok(address=""):
        return {"ip": address, "version": "IPv4"}

    monkeypatch.setattr(app, "DETAILS_PROVIDERS", [primary_fails, backup_ok])

    result = app.lookup_ip("8.8.8.8")
    assert result == {"ip": "8.8.8.8", "version": "IPv4"}


def test_lookup_ip_raises_when_all_providers_fail(monkeypatch):
    def fail1(address=""):
        raise app.ApiError("provider 1 down")

    def fail2(address=""):
        raise app.ApiError("provider 2 down")

    monkeypatch.setattr(app, "DETAILS_PROVIDERS", [fail1, fail2])

    with pytest.raises(app.ApiError, match="provider 2 down"):
        app.lookup_ip("8.8.8.8")


# ---------------------------------------------------------------------------
# safe_lookup: never raises, always returns something
# ---------------------------------------------------------------------------
def test_safe_lookup_returns_bare_address_on_total_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        app, "lookup_ip",
        lambda address: (_ for _ in ()).throw(app.ApiError("all providers down")),
    )

    result = app.safe_lookup("8.8.8.8")

    assert result == {"ip": "8.8.8.8", "version": "IPv4"}
    assert "Warning" in capsys.readouterr().err


def test_safe_lookup_detects_ipv6_version(monkeypatch):
    monkeypatch.setattr(
        app, "lookup_ip",
        lambda address: (_ for _ in ()).throw(app.ApiError("down")),
    )

    result = app.safe_lookup("2001:4860:4860::8888")
    assert result["version"] == "IPv6"


# ---------------------------------------------------------------------------
# fetch_url / fetch_json (requests layer)
# ---------------------------------------------------------------------------
def test_fetch_url_success(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "8.8.8.8"
    mock_response.raise_for_status = lambda: None
    monkeypatch.setattr(app.requests, "get", lambda *a, **k: mock_response)

    assert app.fetch_url("https://api.ipify.org") == "8.8.8.8"


def test_fetch_url_rate_limited(monkeypatch):
    mock_response = MagicMock()
    mock_response.status_code = 429
    monkeypatch.setattr(app.requests, "get", lambda *a, **k: mock_response)

    with pytest.raises(app.ApiError, match="Rate limit"):
        app.fetch_url("https://ipapi.co/json/")


def test_fetch_url_timeout(monkeypatch):
    def raise_timeout(*a, **k):
        raise app.requests.exceptions.Timeout()

    monkeypatch.setattr(app.requests, "get", raise_timeout)

    with pytest.raises(app.ApiError, match="timed out"):
        app.fetch_url("https://ipapi.co/json/")


def test_fetch_url_connection_error(monkeypatch):
    def raise_conn_error(*a, **k):
        raise app.requests.exceptions.ConnectionError("forcibly closed")

    monkeypatch.setattr(app.requests, "get", raise_conn_error)

    with pytest.raises(app.ApiError, match="Network error"):
        app.fetch_url("https://ipapi.co/json/")


def test_fetch_json_invalid_json(monkeypatch):
    monkeypatch.setattr(app, "fetch_url", lambda url: "not valid json")

    with pytest.raises(app.ApiError, match="Could not read"):
        app.fetch_json("https://ipapi.co/json/")


# ---------------------------------------------------------------------------
# Address validation (used in main() before calling any API)
# ---------------------------------------------------------------------------
def test_private_address_is_not_global():
    address = ipaddress.ip_address("192.168.1.1")
    assert address.is_global is False


def test_public_address_is_global():
    address = ipaddress.ip_address("8.8.8.8")
    assert address.is_global is True


def test_invalid_address_raises_value_error():
    with pytest.raises(ValueError):
        ipaddress.ip_address("999.999.999.999")


# ---------------------------------------------------------------------------
# display_info formatting
# ---------------------------------------------------------------------------
def test_display_info_shows_na_for_missing_fields(capsys):
    app.display_info("TEST TITLE", {"ip": "8.8.8.8"}, use_color=False)

    output = capsys.readouterr().out
    assert "TEST TITLE" in output
    assert "8.8.8.8" in output
    assert "N/A" in output
