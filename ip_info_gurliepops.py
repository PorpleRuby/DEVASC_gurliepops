"""
IPv4/IPv6 Address Information App
DEVASC Project Activity 3 - Social Coding (Option 2)
Team: Gurliepops (Alyssa Abejuela, Ma. Carla Jane Mangao, Shaula J. Ygbuhay)

A Python command-line tool that displays the public IPv4 and IPv6 addresses
of this computer along with location, ISP/organization, ASN, country code,
and time zone.

USAGE
    python ip.py                 # this computer's public IPv4 and IPv6
    python ip.py --ip 8.8.8.8    # look up any IPv4 or IPv6 address
    python ip.py --json          # raw JSON output (good for scripts)
    python ip.py --no-color      # plain text output
    python ip.py --help          # show all options

REQUIREMENTS
    Python 3.8+. Uses only the standard library (no pip install needed).

HOW IT WORKS
    1. api.ipify.org   -> public IPv4 address
    2. api6.ipify.org  -> public IPv6 address (fails if there is no IPv6)
    3. ipwho.is        -> details (city, ISP, ASN...) for each address
    If steps 1 and 2 both fail, we ask ipwho.is to detect the address itself.

HOW TO EXTEND
    - New output field: add a (label, json_key) pair to DISPLAY_FIELDS and
      add the matching key in lookup_ip().
    - Different details provider: only lookup_ip() needs to change.

KNOWN LIMITATIONS
    - IP geolocation is approximate; the city may not be the real location.
    - Behind a VPN or proxy, the VPN's public address is shown.
    - Private/reserved addresses (e.g. 192.168.x.x) have no public details.

BACKLOG (future enhancements for Project Activity 4)
    - Export results to a CSV or text file
    - Show the reverse-DNS hostname of each address
    - Flag whether the address belongs to a VPN, proxy, or hosting provider
    - Batch lookup of many addresses from a file
    - Backup details API if ipwho.is is down or rate-limited
    - Show latitude/longitude with a map link
    - GUI or web version for technicians who prefer not to use a terminal
"""

import argparse
import ipaddress
import json
import socket
import sys
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IPV4_API = "https://api.ipify.org"
IPV6_API = "https://api6.ipify.org"
DETAILS_API = "https://ipwho.is/{}"  # empty address = this computer's own
TIMEOUT_SECONDS = 10

# (label shown to the user, key in the dictionary returned by lookup_ip)
DISPLAY_FIELDS = [
    ("IP Address", "ip"),
    ("Version", "version"),
    ("City", "city"),
    ("Region", "region"),
    ("Country", "country_code"),
    ("ISP/Org", "org"),
    ("ASN", "asn"),
    ("Timezone", "timezone"),
]


class ApiError(Exception):
    """Raised when an API call fails in a way we can explain to the user."""


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------
def fetch_url(url):
    """Download a URL with urllib and return the response body as text."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8").strip()
    except urllib.error.HTTPError as err:  # must come before URLError
        if err.code == 429:
            raise ApiError("Rate limit exceeded (HTTP 429). Try again later.")
        raise ApiError(f"HTTP error {err.code}: {err.reason}")
    except (socket.timeout, TimeoutError):
        raise ApiError("Connection timed out.")
    except urllib.error.URLError as err:
        raise ApiError(f"Network error: {err.reason}")
    except OSError as err:  # any other low-level network failure
        raise ApiError(f"Network error: {err}")


def get_public_ip(url):
    """
    Return this computer's public address from an ipify endpoint, or None.

    Not having IPv4 or IPv6 is normal, so this never raises.
    """
    try:
        address = fetch_url(url)
        ipaddress.ip_address(address)  # validates the text is a real address
        return address
    except (ApiError, ValueError):
        return None


def lookup_ip(address=""):
    """
    Get details for an address from ipwho.is ("" = this computer's own).

    Returns a dictionary with the keys used in DISPLAY_FIELDS.
    Raises ApiError with a readable message if something goes wrong.
    """
    raw = fetch_url(DETAILS_API.format(address))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ApiError("Could not read the response from the details API.")
    if not data.get("success", False):
        raise ApiError(data.get("message", "Invalid IP or API error."))

    # ipwho.is nests some values, so pull them out into a flat dictionary.
    connection = data.get("connection") or {}
    timezone = data.get("timezone") or {}
    asn = connection.get("asn")
    return {
        "ip": data.get("ip"),
        "version": data.get("type"),
        "city": data.get("city"),
        "region": data.get("region"),
        "country_code": data.get("country_code"),
        "org": connection.get("org") or connection.get("isp"),
        "asn": f"AS{asn}" if asn else None,
        "timezone": timezone.get("id"),
    }


def safe_lookup(address):
    """
    Like lookup_ip(), but if the details lookup fails (for example the API is
    rate-limited) we still return the bare address so the user sees something.
    """
    try:
        return lookup_ip(address)
    except ApiError as err:
        print(f"Warning: could not get details for {address}: {err}",
              file=sys.stderr)
        version = "IPv6" if ":" in address else "IPv4"
        return {"ip": address, "version": version}


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display_info(title, data, use_color=True):
    """Print one table of details."""
    if use_color:
        cyan, yellow, reset = "\033[96m", "\033[93m", "\033[0m"
    else:
        cyan = yellow = reset = ""

    width = 45
    print(f"\n{cyan}{'=' * width}")
    print(title.center(width))
    print(f"{'=' * width}{reset}")
    for label, key in DISPLAY_FIELDS:
        value = data.get(key)
        if value in (None, ""):
            value = "N/A"
        print(f"{yellow}{label:<12}{reset}: {value}")
    print(f"{cyan}{'=' * width}{reset}")


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Display public IPv4/IPv6 address information."
    )
    parser.add_argument("--ip", help="look up a specific IPv4 or IPv6 address")
    parser.add_argument("--json", action="store_true",
                        help="print raw JSON instead of tables")
    parser.add_argument("--no-color", action="store_true",
                        help="disable colored output")
    return parser.parse_args()


def main():
    args = parse_args()
    use_color = not args.no_color and sys.stdout.isatty()
    results = {}  # title -> details dict

    try:
        if args.ip:
            # Check the address before calling any API.
            try:
                address = ipaddress.ip_address(args.ip)
            except ValueError:
                print(f"[ERROR] '{args.ip}' is not a valid IPv4 or IPv6 address.",
                      file=sys.stderr)
                return 2
            if not address.is_global:
                print(f"[ERROR] '{args.ip}' is a private or reserved address "
                      "and has no public information.", file=sys.stderr)
                return 2
            results["LOOKUP RESULT"] = lookup_ip(args.ip)
        else:
            # Status goes to stderr so it never mixes with --json output.
            print("Detecting public IP addresses...", file=sys.stderr)
            ipv4 = get_public_ip(IPV4_API)
            ipv6 = get_public_ip(IPV6_API)

            if ipv4:
                results["PUBLIC IPv4 INFORMATION"] = safe_lookup(ipv4)
            if ipv6:
                results["PUBLIC IPv6 INFORMATION"] = safe_lookup(ipv6)
            if not results:
                # ipify failed for both; let the details API detect the address.
                results["PUBLIC IP INFORMATION"] = lookup_ip()
    except ApiError as err:
        # Errors go to stderr so --json output stays clean for scripts.
        print(f"\n[ERROR] {err}\n", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    for title, data in results.items():
        display_info(title, data, use_color)

    if not args.ip:
        names = " ".join(results)
        if "IPv4" not in names and "PUBLIC IP INFORMATION" not in names:
            print("\nIPv4: not available on this network")
        if "IPv6" not in names and "PUBLIC IP INFORMATION" not in names:
            print("\nIPv6: not available on this network")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())