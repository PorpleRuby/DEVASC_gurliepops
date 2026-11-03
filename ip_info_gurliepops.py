
"""
IPv4/IPv6 Address Information App
DEVASC Project Activity 3 - Social Coding (Option 2)

Team: Gurliepops
Members:
- Alyssa Abejuela
- Ma. Carla Jane Mangao
- Shaula J. Ygbuhay

DESCRIPTION:
A Python command-line application that detects the computer's public
IPv4 and IPv6 addresses and retrieves geographical and network information.

FEATURES:
- Automatic public IPv4 and IPv6 detection
- Manual IPv4 and IPv6 lookup
- Country, region, city, and continent information
- ISP, organization, and ASN information
- Country flag
- Latitude and longitude
- Timezone and UTC offset
- Formatted colored table output
- JSON output
- CSV export
- Input validation and error handling
- Automatic API fallback

REQUIREMENTS:
Python 3.8 or newer.
Uses only Python standard libraries. No pip installation required.

USAGE:
    python ip_info_gurliepops.py
    python ip_info_gurliepops.py --ip 8.8.8.8
    python ip_info_gurliepops.py --json
    python ip_info_gurliepops.py --no-color
    python ip_info_gurliepops.py --csv results.csv
    python ip_info_gurliepops.py --help
"""

import argparse
import csv
import ipaddress
import json
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IPV4_API = "https://api.ipify.org"
IPV6_API = "https://api6.ipify.org"

DETAILS_API = "https://ipwho.is/{}"
SELF_API = "https://ipwho.is/"

TIMEOUT_SECONDS = 10

# Labels displayed in the application and their corresponding dictionary keys.
DISPLAY_FIELDS = [
    ("IP Address", "ip"),
    ("Version", "version"),
    ("Country Flag", "flag"),
    ("Country", "country"),
    ("Country Code", "country_code"),
    ("Continent", "continent"),
    ("City", "city"),
    ("Region", "region"),
    ("Postal Code", "postal_code"),
    ("ISP", "isp"),
    ("Organization", "org"),
    ("ASN", "asn"),
    ("Network Domain", "domain"),
    ("Timezone", "timezone"),
    ("UTC Offset", "utc_offset"),
    ("Latitude", "latitude"),
    ("Longitude", "longitude"),
]


# ---------------------------------------------------------------------------
# Custom API Exception
# ---------------------------------------------------------------------------

class ApiError(Exception):
    """Raised when an API request fails."""


# ---------------------------------------------------------------------------
# Network Helpers
# ---------------------------------------------------------------------------

def fetch_url(url):
    """Download a URL and return its response as text."""

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=TIMEOUT_SECONDS
        ) as response:

            return response.read().decode("utf-8").strip()

    except urllib.error.HTTPError as err:
        if err.code == 429:
            raise ApiError(
                "API rate limit exceeded (HTTP 429). Try again later."
            )

        if err.code == 403:
            raise ApiError(
                "Access denied by the API (HTTP 403)."
            )

        raise ApiError(
            f"HTTP error {err.code}: {err.reason}"
        )

    except (socket.timeout, TimeoutError):
        raise ApiError("Connection timed out.")

    except urllib.error.URLError as err:
        raise ApiError(
            f"Network error: {err.reason}"
        )

    except (OSError, UnicodeDecodeError) as err:
        raise ApiError(
            f"Network error: {err}"
        )


def get_public_ip(url):
    """
    Retrieve the computer's public IP address.

    Returns None if the endpoint is unavailable or the response
    is not a valid IPv4 or IPv6 address.
    """

    try:
        address = fetch_url(url)

        # Validate the returned IP address.
        ipaddress.ip_address(address)

        return address

    except (ApiError, ValueError):
        return None


# ---------------------------------------------------------------------------
# IP Information Lookup
# ---------------------------------------------------------------------------

def lookup_ip(address=""):
    """
    Retrieve geographical and network information using ipwho.is.

    If address is empty, the API automatically detects the
    computer's current public IP address.

    Returns a dictionary containing the information used by
    DISPLAY_FIELDS.
    """

    if address:
        # Encode the address safely for the API URL.
        encoded_address = urllib.parse.quote(address, safe=":")
        url = DETAILS_API.format(encoded_address)
    else:
        url = SELF_API

    raw = fetch_url(url)

    try:
        data = json.loads(raw)

    except json.JSONDecodeError:
        raise ApiError(
            "Could not read the JSON response from the details API."
        )

    # Check whether the API successfully processed the request.
    if not data.get("success", False):
        raise ApiError(
            data.get("message", "Invalid IP address or API error.")
        )

    # Extract nested information.
    connection = data.get("connection") or {}
    timezone = data.get("timezone") or {}
    flag = data.get("flag") or {}

    # Format the ASN.
    asn = connection.get("asn")

    if asn:
        asn = str(asn)

        if not asn.upper().startswith("AS"):
            asn = f"AS{asn}"

    # Determine the IP version.
    ip_type = data.get("type")

    if not ip_type and data.get("ip"):
        ip_type = f"IPv{ipaddress.ip_address(data['ip']).version}"

    # Return a simplified dictionary for easier display and export.
    return {
        "ip": data.get("ip") or address,
        "version": ip_type,
        "flag": flag.get("emoji"),
        "country": data.get("country"),
        "country_code": data.get("country_code"),
        "continent": data.get("continent"),
        "city": data.get("city"),
        "region": data.get("region"),
        "postal_code": data.get("postal"),
        "isp": connection.get("isp"),
        "org": connection.get("org"),
        "asn": asn,
        "domain": connection.get("domain"),
        "timezone": timezone.get("id"),
        "utc_offset": timezone.get("utc"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
    }


def safe_lookup(address):
    """
    Retrieve IP details without losing the IP address if the
    details API fails.

    This allows the application to display the detected IP
    even when additional information is unavailable.
    """

    try:
        return lookup_ip(address)

    except ApiError as err:
        print(
            f"Warning: Could not retrieve details for {address}: {err}",
            file=sys.stderr
        )

        version = f"IPv{ipaddress.ip_address(address).version}"

        return {
            "ip": address,
            "version": version
        }


# ---------------------------------------------------------------------------
# Display Functions
# ---------------------------------------------------------------------------

def display_status(ipv4, ipv6, output_stream=None):
    """Display the availability of IPv4 and IPv6."""

    if output_stream is None:
        output_stream = sys.stdout

    print("\nNETWORK DETECTION STATUS", file=output_stream)
    print("=" * 45, file=output_stream)

    if ipv4:
        print("[OK] IPv4 address detected", file=output_stream)
    else:
        print("[!] IPv4 address unavailable", file=output_stream)

    if ipv6:
        print("[OK] IPv6 address detected", file=output_stream)
    else:
        print("[!] IPv6 address unavailable", file=output_stream)

    print("=" * 45, file=output_stream)


def display_info(title, data, use_color=True):
    """Display IP information in a formatted table."""

    if use_color:
        cyan = "\033[96m"
        yellow = "\033[93m"
        green = "\033[92m"
        reset = "\033[0m"
    else:
        cyan = yellow = green = reset = ""

    width = 50

    print(f"\n{cyan}{'=' * width}{reset}")
    print(f"{green}{title.center(width)}{reset}")
    print(f"{cyan}{'=' * width}{reset}")

    for label, key in DISPLAY_FIELDS:
        value = data.get(key)

        if value is None or value == "":
            value = "N/A"

        print(
            f"{yellow}{label:<17}{reset}: {value}"
        )

    print(f"{cyan}{'=' * width}{reset}")


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_csv(results, filename):
    """Save retrieved IP information into a CSV file."""

    try:
        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            # CSV column headings.
            writer.writerow([
                "IP Information",
                "Field",
                "Value"
            ])

            for title, data in results.items():

                # Add a section heading for each IP address.
                writer.writerow([title, "", ""])

                for label, key in DISPLAY_FIELDS:
                    value = data.get(key)

                    if value is None or value == "":
                        value = "N/A"

                    writer.writerow([
                        title,
                        label,
                        value
                    ])

        print(
            f"[SUCCESS] Results saved to: {filename}",
            file=sys.stderr
        )

        return True

    except OSError as err:
        print(
            f"[ERROR] Could not save CSV file: {err}",
            file=sys.stderr
        )

        return False


# ---------------------------------------------------------------------------
# Command-Line Arguments
# ---------------------------------------------------------------------------

def parse_args():
    """Define and process the application's command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Display public IPv4/IPv6 address information."
    )

    parser.add_argument(
        "--ip",
        help="Look up a specific IPv4 or IPv6 address."
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON output instead of formatted tables."
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output."
    )

    parser.add_argument(
        "--csv",
        metavar="FILE",
        help="Save retrieved IP information to a CSV file."
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

def main():
    """Control the execution of the application."""

    args = parse_args()

    # Enable colors only when output is directed to a terminal.
    use_color = (
        not args.no_color
        and sys.stdout.isatty()
    )

    # Store results separately for each detected IP address.
    results = {}

    try:

        # ---------------------------------------------------------------
        # Manual IP Lookup
        # ---------------------------------------------------------------

        if args.ip:

            try:
                # Validate the user-provided IP address.
                ipaddress.ip_address(args.ip)

            except ValueError:
                print(
                    f"[ERROR] '{args.ip}' is not a valid IPv4 or IPv6 address.",
                    file=sys.stderr
                )

                return 2

            print(
                "Looking up IP address...",
                file=sys.stderr
            )

            results["LOOKUP RESULT"] = lookup_ip(args.ip)

        # ---------------------------------------------------------------
        # Automatic Public IP Detection
        # ---------------------------------------------------------------

        else:

            # Send progress messages to stderr so they do not
            # interfere with JSON output.
            print(
                "Detecting public IP addresses...",
                file=sys.stderr
            )

            ipv4 = get_public_ip(IPV4_API)
            ipv6 = get_public_ip(IPV6_API)

            # Display IPv4 and IPv6 availability.
            display_status(
                ipv4,
                ipv6,
                sys.stderr if args.json else sys.stdout
            )

            # Retrieve IPv4 information.
            if ipv4:
                results["PUBLIC IPv4 INFORMATION"] = safe_lookup(ipv4)

            # Retrieve IPv6 information.
            if ipv6:
                results["PUBLIC IPv6 INFORMATION"] = safe_lookup(ipv6)

            # -----------------------------------------------------------
            # Fallback
            # -----------------------------------------------------------

            if not results:

                print(
                    "\nBoth ipify endpoints failed. "
                    "Trying automatic detection through ipwho.is...",
                    file=sys.stderr
                )

                results["PUBLIC IP INFORMATION"] = lookup_ip()

        # ---------------------------------------------------------------
        # CSV Export
        # ---------------------------------------------------------------

        if args.csv:
            if not export_csv(results, args.csv):
                return 1

        # ---------------------------------------------------------------
        # JSON Output
        # ---------------------------------------------------------------

        if args.json:
            print(
                json.dumps(results, indent=2, ensure_ascii=False)
            )

            return 0

        # ---------------------------------------------------------------
        # Formatted Table Output
        # ---------------------------------------------------------------

        for title, data in results.items():
            display_info(
                title,
                data,
                use_color
            )

        print()

        return 0

    except ApiError as err:

        print(
            f"\n[ERROR] {err}\n",
            file=sys.stderr
        )

        return 1


# ---------------------------------------------------------------------------
# Program Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
