"""
IPv4/IPv6 Address Information App
DEVASC Project Activity 3 – Social Coding (Option 2)
Team: Gurliepops (Alyssa Abejuela, Ma. Carla Jane Mangao, Shaula J. YgbuHay)

A Python command-line tool that displays public IPv4 and IPv6 addresses
along with location, ISP/organization, ASN, country code, and time zone.
"""

import sys
import json
import urllib.request
import urllib.error

# Configuration
IPV4_API = "https://api.ipify.org"
IPV6_API = "https://api6.ipify.org"
DETAILS_API = "https://ipapi.co/{}/json/"

DISPLAY_FIELDS = [
    ("IPv4", "ip"),
    ("City", "city"),
    ("Region", "region"),
    ("Country", "country_code"),
    ("ISP/Org", "org"),
    ("ASN", "asn"),
    ("Timezone", "timezone")
]

class ApiError(Exception):
    """Custom exception for API failures."""
    pass

def fetch_url(url):
    """Helper to fetch data from a URL using built-in urllib."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8').strip()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise ApiError("Rate limit exceeded (HTTP 429). Please try again later.")
        raise ApiError(f"HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ApiError(f"Network error: {e.reason}")
    except TimeoutError:
        raise ApiError("Connection timed out.")

def lookup_ip(ip_address=""):
    """Fetches detailed info for a specific IP or the current IP."""
    url = DETAILS_API.format(ip_address) if ip_address else "https://ipapi.co/json/"
    try:
        raw_data = fetch_url(url)
        data = json.loads(raw_data)
        if data.get("error"):
            raise ApiError(data.get("reason", "Invalid IP or API error."))
        return data
    except json.JSONDecodeError:
        raise ApiError("Failed to parse JSON response from details API.")

def display_info(data, use_color=True):
    """Formats and prints the data in a table."""
    if use_color:
        CYAN, YELLOW, RESET = "\033[96m", "\033[93m", "\033[0m"
    else:
        CYAN = YELLOW = RESET = ""

    width = 45
    print(f"\n{CYAN}{'=' * width}")
    print("        IP ADDRESS INFORMATION".center(width))
    print(f"{'=' * width}{RESET}")
    
    for label, key in DISPLAY_FIELDS:
        value = data.get(key, "N/A")
        if value is None:
            value = "N/A"
        print(f"{YELLOW}{label:<12}{RESET}: {value}")
        
    print(f"{CYAN}{'=' * width}{RESET}\n")

def main():
    # Handle Command Line Arguments
    args = sys.argv[1:]
    target_ip = ""
    output_json = False
    use_color = True

    if "--json" in args:
        output_json = True
    if "--no-color" in args:
        use_color = False
    if "--ip" in args:
        try:
            ip_index = args.index("--ip") + 1
            target_ip = args[ip_index]
        except IndexError:
            print("Error: --ip requires an address (e.g., --ip 8.8.8.8)")
            sys.exit(1)

    try:
        if target_ip:
            # Look up specific IP
            data = lookup_ip(target_ip)
            if output_json:
                print(json.dumps(data, indent=2))
            else:
                display_info(data, use_color)
        else:
            # Try auto-detect IPv4 and IPv6
            print("Detecting public IP addresses...")
            ipv4, ipv6 = None, None
            
            try: ipv4 = fetch_url(IPV4_API)
            except ApiError: pass
            
            try: ipv6 = fetch_url(IPV6_API)
            except ApiError: pass

            if not ipv4 and not ipv6:
                # Fallback
                data = lookup_ip()
            else:
                data = lookup_ip(ipv4 if ipv4 else ipv6)
                # Inject the IPv4/IPv6 we found
                data['ip'] = ipv4 if ipv4 else "N/A"
                if ipv6:
                    data['ipv6'] = ipv6

            if output_json:
                print(json.dumps(data, indent=2))
            else:
                display_info(data, use_color)
                if ipv6 and not output_json:
                    print(f"{'IPv6':<12}: {ipv6}\n")

    except ApiError as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()