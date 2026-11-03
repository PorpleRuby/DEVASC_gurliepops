# IPv4/IPv6 Address Information App

**DEVASC Project Activity 3 - Social Coding (Option 2: New Application)**

Team: **Gurliepops**
- Alyssa Margarette D. Abejuela — Scrum Leader / Project Manager
- Ma. Carla Jane D. Mangao — Developer (Python, REST API integration, JSON parsing, terminal output formatting)
- Shaula J. Ygbuhay — Developer (Python, error handling, technical documentation, pytest unit testing)

## Overview

A Python command-line tool that retrieves and displays a computer's public
IPv4 and IPv6 address information — city, region, country code, ISP/org,
ASN, and time zone — using the **ipapi.co** REST API, with **ipwho.is** as
an automatic backup if the main API fails or is rate-limited.

Built for the engineering department's request to give network technicians
a quick, readable summary of their public IP addressing information.

## Features

- Detects this computer's public IPv4 and IPv6 addresses automatically
- Looks up any specific IPv4 or IPv6 address with `--ip`
- Clean, color-coded table output (or plain text with `--no-color`)
- Raw JSON output for scripting with `--json`
- Rejects private/reserved addresses (e.g. `192.168.x.x`) before calling any API
- Falls back to a second API provider automatically if the main one fails
- Clear, user-facing error messages instead of raw stack traces
- 17 automated pytest unit tests covering parsing, fallback, and error handling

## Requirements

- Python 3.8+
- The third-party `requests` library

## Setup

1. Clone the repository and switch to this branch:
   ```
   git clone https://github.com/PorpleRuby/DEVASC_gurliepops.git
   cd DEVASC_gurliepops
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

```
python ip_info_gurliepops.py                # this computer's public IPv4 and IPv6
python ip_info_gurliepops.py --ip 8.8.8.8    # look up any IPv4 or IPv6 address
python ip_info_gurliepops.py --json          # raw JSON output (good for scripts)
python ip_info_gurliepops.py --no-color      # plain text output
python ip_info_gurliepops.py --help          # show all options
```

## Running the tests

```
python -m pytest test_ip_info_gurliepops.py -v
```

All 17 tests mock the network layer, so they run instantly and do not
depend on the live APIs or on rate limits.

## How it works

1. `api.ipify.org` → this computer's public IPv4 address
2. `api6.ipify.org` → this computer's public IPv6 address (fails gracefully if there is no IPv6)
3. `ipapi.co` → details (city, ISP, ASN, time zone...) for each address — main provider, no API key required
4. `ipwho.is` → backup details provider, used automatically if ipapi.co fails or is rate-limited

If steps 1 and 2 both fail (no outbound ipify access), the app asks the
details APIs to detect the caller's address directly.

## Project structure

```
ip_info_gurliepops.py       Main application
test_ip_info_gurliepops.py  Pytest unit tests
requirements.txt            Python dependencies
README.md                   This file
```

## How to extend

- **New output field:** add a `(label, json_key)` pair to `DISPLAY_FIELDS`
  and add the matching key in both `lookup_ipapi()` and `lookup_ipwhois()`.
- **New details provider:** write a `lookup_<name>()` function that returns
  the same dictionary keys, then add it to `DETAILS_PROVIDERS`.

## Known limitations

- IP geolocation is approximate; the city shown may not be the exact real location.
- Behind a VPN or proxy, the VPN's public address is shown instead of the real one.
- Private/reserved addresses have no public details and are rejected before any API call.
- Free APIs rate-limit requests; running the app many times in a row may
  cause `N/A` fields until the limit resets, even with the backup provider.

## Backlog (future enhancements)

- Export results to a CSV or text file
- Show the reverse-DNS hostname of each address
- Flag whether the address belongs to a VPN, proxy, or hosting provider
- Batch lookup of many addresses from a file
- Cache results for a few minutes to avoid hitting API limits
- Show latitude/longitude with a map link
- GUI or web version for technicians who prefer not to use a terminal

## GitHub workflow

- `main` holds the starter code and this README.
- Each member works on their own feature branch (e.g. `feature/api-request`,
  `feature/output-formatting`, `feature/error-handling`).
- Finished work is pushed and opened as a pull request into `main`, reviewed
  by at least one teammate, and merged after approval. Feature branches are
  deleted after merge.
