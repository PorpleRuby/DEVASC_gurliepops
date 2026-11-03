# IPv4/IPv6 Address Information App

DEVASC Project Activity 3 – Social Coding (Option 2)

A Python command-line tool that displays this computer's current public IPv4 and IPv6 addresses along with location, ISP/organization, ASN, country code, and time zone. It is meant to give network technicians a quick, readable summary.

## Setup


pip install requests
python ip_info_gurliepops.py


Requires Python 3.8 or newer. No API key is needed.

## Usage

 Command and What it does 

 `python ip_info_gurliepops.py` => Shows details for this computer's public IPv4 and IPv6 addresses 
 `python ip_info_gurliepops.py --ip 8.8.8.8` => Looks up any IPv4 or IPv6 address 
 `python ip_info_gurliepops.py --json` => Prints raw JSON instead of tables 
 `python ip_info_gurliepops.py --no-color` => Turns off colored output 

## Features

- Finds both the public IPv4 and IPv6 address
- Formatted, colored table output (color turns off automatically when piped to a file)
- Look up any address with `--ip`, with input validation
- JSON output mode for use in other scripts
- Error handling for no internet, timeouts, rate limits (HTTP 429), bad responses, and missing IPv6

## How it works

1. `api.ipify.org` returns the public IPv4 address.
2. `api6.ipify.org` returns the public IPv6 address (fails gracefully if the network has no IPv6).
3. `ipapi.co/<address>/json/` returns the details for each address.
4. If steps 1 and 2 both fail, the app falls back to `ipapi.co/json/`, which detects the address itself.

## Code guide for the next team

- `ip_info_gurliepops.py` is a single file, organized top to bottom: configuration, API functions, display functions, then `main()`.
- To add a new field to the output, add a `(label, json_key)` pair to `DISPLAY_FIELDS`.
- To switch details providers, only `lookup_ip()` needs to change.
- Errors from the details API are raised as `ApiError` and caught in `main()`.

## Known limitations

- ipapi.co's free tier has a daily request limit, so heavy use may hit HTTP 429.
- Behind a VPN or proxy, the app shows the VPN's public address, not the computer's real one.
- Location data is approximate and based on the IP address.

## Backlog (future enhancements)

1. Save results to a CSV or text file
2. Show local/private IP addresses alongside public ones
3. Lookup history log with timestamps
4. Batch lookup from a file of addresses
5. Fallback to a second details API when rate-limited
6. Simple GUI or web interface
7. Unit tests using mocked API responses
8. Caching to reduce API calls
9. Detect VPN/proxy usage
10. Package as an installable tool (`pip install`)
