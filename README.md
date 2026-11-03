
# IPv4/IPv6 Address Information App

**DEVASC Project Activity 3 – Social Coding (Option 2: New Code)**

**Team:** Gurliepops

**Team Members:**
- Alyssa Abejuela
- Ma. Carla Jane Mangao
- Shaula J. Ygbuhay

---

## 1. Project Overview

The IPv4/IPv6 Address Information App is a Python command-line application designed to provide network technicians with information about public IP addresses.

The application automatically detects the computer's current public IPv4 and IPv6 addresses and retrieves additional geographical and network information, including country, region, city, ISP, organization, ASN, timezone, and approximate geographical coordinates.

Users can also manually look up specific IPv4 or IPv6 addresses and choose between formatted table output, JSON output, or CSV file export.

The application aims to provide a simple and convenient tool that helps network technicians retrieve and organize public IP addressing information.

## 2. Project Objectives

The main objectives of this project are to:

- Automatically retrieve the computer's current public IPv4 and IPv6 addresses.
- Retrieve geographical and network information associated with an IP address.
- Allow users to manually look up specific IPv4 and IPv6 addresses.
- Display information in an organized and readable format.
- Provide JSON output for integration with other applications and scripts.
- Allow users to export retrieved information into CSV files.
- Validate IP addresses before performing manual lookups.
- Handle network errors, API failures, and unavailable IP versions.

## 3. Application Features

The application includes the following features:

| Feature | Description |
|---|---|
| Public IPv4 Detection | Automatically retrieves the computer's public IPv4 address. |
| Public IPv6 Detection | Attempts to retrieve the computer's public IPv6 address. |
| Manual IP Lookup | Allows users to look up a specific IPv4 or IPv6 address using the `--ip` argument. |
| IP Information Lookup | Retrieves geographical and network information using ipwho.is. |
| Network Detection Status | Displays whether IPv4 and IPv6 addresses are available. |
| Country Information | Displays the country name, country code, and country flag when available. |
| Geolocation Information | Displays continent, city, region, postal code, latitude, and longitude. |
| ISP and Organization | Displays the Internet Service Provider and associated organization. |
| ASN Information | Displays the Autonomous System Number. |
| Timezone Information | Displays the timezone and UTC offset. |
| Formatted Table Output | Displays information in organized tables with colored headings and labels. |
| JSON Output | Displays retrieved information in JSON format using the `--json` argument. |
| CSV Export | Saves retrieved information into a CSV file using the `--csv` argument. |
| No-Color Mode | Allows users to disable colored output using the `--no-color` argument. |
| Input Validation | Checks whether manually entered IP addresses are valid. |
| Error Handling | Handles connection timeouts, HTTP errors, API rate limits, and invalid responses. |
| Automatic API Fallback | Uses ipwho.is to detect the computer's IP if both ipify endpoints fail. |

## 4. Information Displayed

For each successfully retrieved IP address, the application can display:

| Information | Description |
|---|---|
| IP Address | The public IPv4 or IPv6 address. |
| Version | Identifies whether the address uses IPv4 or IPv6. |
| Country Flag | Displays the corresponding country flag emoji when available. |
| Country | The complete country name. |
| Country Code | The two-letter country code. |
| Continent | The continent associated with the IP address. |
| City | The approximate city associated with the IP address. |
| Region | The geographical region or state. |
| Postal Code | The associated postal or ZIP code. |
| ISP | The Internet Service Provider. |
| Organization | The organization associated with the IP address. |
| ASN | The Autonomous System Number. |
| Network Domain | The domain associated with the network organization. |
| Timezone | The timezone associated with the IP address location. |
| UTC Offset | The time difference from Coordinated Universal Time. |
| Latitude | The approximate geographical latitude. |
| Longitude | The approximate geographical longitude. |

**Note:** Some fields may display as `N/A` depending on the information returned by the API.

## 5. Technologies and APIs Used

### Programming Language

- Python 3.8 or newer

### Python Libraries

The application uses Python's built-in standard libraries. No additional package installation is required.

| Library | Purpose |
|---|---|
| `argparse` | Handles command-line arguments and user options. |
| `csv` | Exports retrieved IP information into CSV files. |
| `ipaddress` | Validates IPv4 and IPv6 addresses. |
| `json` | Processes API responses and generates JSON output. |
| `socket` | Handles network-related exceptions. |
| `sys` | Handles command-line output, error messages, and program exit codes. |
| `urllib.error` | Handles HTTP and URL-related errors. |
| `urllib.parse` | Encodes IP addresses for API requests. |
| `urllib.request` | Sends HTTP requests to external APIs. |

### External APIs

**1. ipify**

Used to retrieve the computer's current public IP addresses.

- IPv4 Endpoint: `https://api.ipify.org`
- IPv6 Endpoint: `https://api6.ipify.org`

**2. ipwho.is**

Used to retrieve geographical and network information associated with an IP address.

- Specific IP Lookup: `https://ipwho.is/{ip}`
- Automatic IP Detection: `https://ipwho.is/`

The application does not require an API key for the selected ipwho.is endpoint.

## 6. Installation and Setup

### Prerequisites

Before running the application, make sure you have:

- Python 3.8 or newer installed.
- An active internet connection.
- The project source code downloaded or cloned from GitHub.

### Step 1: Clone the Repository

Open the VS Code terminal and execute:

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
```

Replace `YOUR_GITHUB_REPOSITORY_LINK` with the actual GitHub repository URL.

### Step 2: Navigate to the Project Folder

```bash
cd YOUR_PROJECT_FOLDER
```

### Step 3: Run the Application

```bash
python ip_info_gurliepops.py
```

**Important:** The application uses only Python's standard libraries. No `pip install` command or additional Python package is required.

## 7. How to Use the Application

The application supports several command-line options.

### A. Display Public IPv4 and IPv6 Information

```bash
python ip_info_gurliepops.py
```

Automatically detects the computer's public IPv4 and IPv6 addresses.

The application displays a network detection status summary followed by the available IP information.

### B. Look Up a Specific IP Address

```bash
python ip_info_gurliepops.py --ip 8.8.8.8
```

Retrieves information for the specified IPv4 address.

You can also look up an IPv6 address by providing it after the `--ip` argument.

### C. Display JSON Output

```bash
python ip_info_gurliepops.py --json
```

Displays the retrieved information in JSON format instead of formatted tables.

This option is useful when the output needs to be processed by another application or script.

### D. Disable Colored Output

```bash
python ip_info_gurliepops.py --no-color
```

Displays the information without colored text.

### E. Export Information to CSV

```bash
python ip_info_gurliepops.py --csv results.csv
```

Saves the retrieved IP information into a CSV file named `results.csv`.

The file can be opened using Microsoft Excel or other spreadsheet applications.

### F. Export CSV and Display JSON

```bash
python ip_info_gurliepops.py --json --csv results.csv
```

Exports the retrieved information to a CSV file while also displaying JSON output in the terminal.

### G. Display Available Commands

```bash
python ip_info_gurliepops.py --help
```

Displays all available command-line arguments and their descriptions.

## 8. How the Application Works

The application follows these steps when retrieving the computer's public IP information:

1. **IPv4 Detection:** Sends a request to `api.ipify.org` to retrieve the public IPv4 address.
2. **IPv6 Detection:** Sends a request to `api6.ipify.org` to retrieve the public IPv6 address.
3. **Address Validation:** Uses Python's `ipaddress` module to verify that the retrieved addresses are valid.
4. **Network Status:** Displays whether IPv4 and IPv6 addresses are available.
5. **Information Retrieval:** Sends each available IP address to `ipwho.is` to retrieve additional network and geographical information.
6. **Data Processing:** Converts the API responses into Python dictionaries using the JSON module.
7. **Information Display:** Organizes the retrieved information into formatted tables or JSON output.
8. **CSV Export:** If requested, saves the retrieved information into a CSV file.
9. **Fallback Mechanism:** If both ipify endpoints fail, the application attempts to use `ipwho.is` to automatically detect the computer's public IP address.

The application also handles situations where an IP version is unavailable or an API request fails.

## 9. Code Structure and Documentation

The application is contained in a single Python file named `ip_info_gurliepops.py`.

The source code is organized into the following sections:

| Function or Section | Description |
|---|---|
| Configuration | Contains API endpoints, timeout settings, and display field definitions. |
| `ApiError` | Custom exception used to handle API-related errors. |
| `fetch_url()` | Sends HTTP requests and handles network-related errors. |
| `get_public_ip()` | Retrieves and validates public IP addresses from ipify. |
| `lookup_ip()` | Retrieves geographical and network information using ipwho.is. |
| `safe_lookup()` | Attempts to retrieve IP details while preserving the detected IP address if the details lookup fails. |
| `display_status()` | Displays whether IPv4 and IPv6 addresses are available. |
| `display_info()` | Displays retrieved information in an organized table. |
| `export_csv()` | Saves retrieved IP information into a CSV file. |
| `parse_args()` | Defines and processes command-line options. |
| `main()` | Controls application execution and connects the different functions. |

### Instructions for Future Developers

The application was designed to be easy to maintain and extend.

- **Adding a new information field:** Add a `(label, json_key)` pair to `DISPLAY_FIELDS` and update the return dictionary in `lookup_ip()`.
- **Changing the details provider:** Modify `lookup_ip()` to use another API and map its response fields.
- **Changing the output format:** Modify `display_info()`.
- **Changing the CSV format:** Modify `export_csv()`.
- **Adding command-line options:** Add new arguments inside `parse_args()`.
- **Improving error handling:** Update the `ApiError` exception handling and relevant network functions.

Comments and function documentation are included throughout the source code to help future developers understand the application's functionality.

## 10. Error Handling and Known Limitations

### Error Handling

The application accounts for common problems, including:

- Invalid IPv4 or IPv6 addresses.
- No internet connection.
- Connection timeouts.
- HTTP errors.
- API rate limits (HTTP 429).
- Access denied responses (HTTP 403).
- Invalid or unreadable API responses.
- Unavailable IPv6 connectivity.
- Missing information from the details API.
- CSV file creation or writing errors.

When an IP details lookup fails during automatic detection, the application attempts to display the available IP address instead of terminating the entire lookup process.

### Known Limitations

1. **API Request Limits:** The selected API has usage limits. Excessive requests may result in HTTP 429 errors.
2. **VPN and Proxy Usage:** When connected to a VPN or proxy, the application may display the public IP address of that service instead of the user's original public IP address.
3. **Approximate Geolocation:** IP-based geographical information is not always precise and may not represent the computer's actual physical location.
4. **IPv6 Availability:** Some networks do not support IPv6, so the application may only display IPv4 information.
5. **Internet Dependency:** An active internet connection is required to communicate with external APIs.
6. **API Availability:** The application's functionality depends on the availability and response of ipify and ipwho.is.
7. **CSV Export:** Exporting to an existing filename overwrites its previous contents.

## 11. Project Backlog (Future Enhancements)

The following features are proposed for future versions of the application. They are not included in the current implementation.

| No. | Backlog Item | Description |
|---|---|---|
| 1 | Private IP Detection | Display the computer's local/private IP addresses alongside its public IP addresses. |
| 2 | Lookup History | Maintain a history of previous IP lookups with timestamps. |
| 3 | Batch IP Lookup | Allow users to retrieve information for multiple IP addresses from a file. |
| 4 | Secondary API Provider | Add another IP information API as a fallback when the primary provider is unavailable or rate-limited. |
| 5 | Graphical User Interface | Develop a simple GUI or web-based interface instead of relying only on the command line. |
| 6 | Automated Unit Testing | Implement unit tests using mocked API responses to verify application functionality. |
| 7 | Response Caching | Store previous lookup results temporarily to reduce unnecessary API requests. |
| 8 | VPN/Proxy Detection | Add functionality to identify possible VPN or proxy connections, if supported by the selected provider. |
| 9 | IP Address Comparison | Allow users to compare geographical and network information from two or more IP addresses. |
| 10 | Application Packaging | Package the application for easier installation and distribution. |

## 12. Team Members and Responsibilities

The project was developed by Team Gurliepops.

| Team Member | Role | Responsibilities |
|---|---|---|
| Alyssa Abejuela | Scrum Leader / Project Coordinator | Coordinates project tasks, monitors progress, assists with development, and ensures that project requirements are completed. |
| Ma. Carla Jane Mangao | Developer | Contributes to application development, code review, testing, and documentation. |
| Shaula J. Ygbuhay | Developer | Contributes to application development, API integration, testing, and documentation. |

All team members participate in project discussions, problem-solving, testing, and application improvements.

## 13. GitHub Collaboration

GitHub is used as the team's collaborative version control platform.

The repository allows team members to access the project source code, contribute changes, and maintain a shared version of the application.

The team uses the following GitHub collaboration practices:

1. **Repository Creation:** A shared repository is created for the project.
2. **Adding Collaborators:** Team members are added to the repository to allow them to contribute.
3. **Branch Creation:** Separate branches are used for individual development tasks.
4. **Code Development:** Team members make changes within their assigned branches.
5. **Pull Requests:** Completed changes are submitted through pull requests for review.
6. **Code Review:** Team members review proposed changes before merging them into the main branch.
7. **Merging:** Approved changes are merged into the main branch to maintain the latest working version of the application.

**GitHub Repository:** [INSERT YOUR GITHUB REPOSITORY LINK HERE]

## 14. Project Reflection

Throughout the development of this application, the team gained experience in working collaboratively on a Python project and using external REST APIs to retrieve public IP addressing information.

One of the challenges was handling different network conditions, particularly when IPv6 was unavailable or when API requests failed. The team addressed these issues by implementing error handling, input validation, and an automatic fallback mechanism.

Another improvement was expanding the application's output to include more geographical and network information and adding JSON and CSV export options.

The project also provided an opportunity to understand how GitHub supports collaborative development through branches, pull requests, code reviews, and merging.

Overall, the activity helped the team improve its Python programming, API integration, debugging, documentation, and teamwork skills.

---

**Project:** IPv4/IPv6 Address Information App

**Course Activity:** DEVASC Project Activity 3 – Social Coding

**Selected Option:** Option 2 – New Code: Create an IPv4/IPv6 Address Application

**Team:** Gurliepops
