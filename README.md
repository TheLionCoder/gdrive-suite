# Gdrive-Suite

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPi Version](https://img.shields.io/pypi/v/gdrive-suite.svg?style=for-the-badge&logo=pypi&color=blue)](https://pypi.org/project/gdrive-suite)
[![MIT License](https://img.shields.io/github/license/TheLionCoder/gdrive-suite?style=for-the-badge&color=green)](https://github.com/TheLionCoder/gdrive-suite/blob/master/LICENSE)
GDrive Suite is a robust Python library designed to streamline interaction with
Google Drive and Google Sheets.
It provides an intuitive, high-level interface over the official Google APIs,
handling authentication, token management, and API calls so you can focus on
your data workflows.

**For a complete guide, usage examples, and the full API reference, please see [GitHub Pages](https://TheLionCoder.github.io/gdrive-suite)**

Whether you're a data engineer building ETL pipelines, a data analyst fetching
the latest reports, or a data scientist accessing datasets, GDrive Suite simplifies
cloud file management.

---

## Features

- **Seamless Authentication**: Handles Oauth2 flow and token refreshing automatically,
  supporting both local server environments (via Application Default Credentials).
- **File Operations**: Easily download, upload, and list files and folders.
- **Google Workspace Conversion**: automatically convert Google Docs, Sheets,
  and slices to formats like `.doc`, `.xlsx`, `.pdf` on download.
- **Path-Based Navigation**: Find files and folders using familiar directory
  paths (e.g., `reports/2025/some_month`).
- **Direct Data Retrieval**: Pull data directly from Google Sheets into your
  python environment.
- **In-Memory File Handling**: Retrieve file content directly into a `BytesIO`
  object for in-memory processing without writing to disk.
  GDrive Suite is a robust Python library designed to streamline interaction with
  Google Drive and Google Sheets.
  It provides an intuitive, high-level interface over the official Google APIs,
  handling authentication, token management, and API calls so you can
  focus on your data workflows.

Whether you're a data engineer building ETL pipelines, a data analyst fetching
the latest reports, or a data scientist accessing datasets,
GDrive Suite simplifies cloud file management.

## Installation

Install `gdrive-suite` directly from PyPi. The library requires Python 3.11
or higher.

```bash
pip install gdrive-suite
```

---

The library requires python 3.11 or higher.

## Configuration

To use GDrive Suite, you need to enable the Google Drive API and obtain credentials
for your application.

1. Enable the Google Drive API

- Go to the Google Cloud Console.

- Create a new project or select an existing one.

- In the navigation menu, go to APIs & Services > Library.

- Search for "Google Drive API" and "Google Sheets API" and enable both.

2. Create Credentials

- In the navigation menu, go to APIs & Services > Credentials.

- Click Create Credentials > OAuth client ID.

- Select Desktop app as the application type.

- Give the client ID a name (e.g., "GDrive Suite Client") and click Create.

- A window will appear. Click Download JSON to download the credentials file.

3. Set Up Your Project

- Rename the downloaded JSON file to google_credentials.json.

- In your project, create a directory to store this file. We recommend conf/local.

- Place the google_credentials.json file in this directory.

Your project structure should look like this:o use Gdrive Suite you need to enable

- Place credentials in `conf/local`

```bash
├── conf
│   └── local
│       ├── credentials.json
├── src
│   ├── script.py

```

The first time you run your application, you will be prompted to authorize it via
a browser window. A `google_token.json` file will then be created in the same directory.
This token will be automatically refreshed as needed.

### Usage Examples

### Basic Usage: Download a file

This example shows how to initialize the client and download a file.

```python
from pathlib import Path
from gdrive_suite import (
  GDriveClient,
  GDriveClientConfig,
  DownloadTarget,
  GDriveSettings
)
# --- 1. Configuration ---
# Define the path to your configuration directory
CONFIG_DIR = Path("conf/local")

# Define the required API scopes
# .readonly is safer if you only need to read files
GOOGLE_SCOPES = [
    ["https://www.googleapis.com/auth/drive.readonly, https://www.googleapis.com/auth/drive.file"]
    # Needed for uploads/modifications
]

# --- 2. Initialization ---
# Create the settings object
gdrive_settings: GDriveSettings(
  config_dir=CONFIG_DIR,
  token_file_name = "google_token.json",
  credentials_file_name = "google_credentials.json",
)
# Create a configuration object
gdrive_config = GDriveClientConfig(
    scope=GOOGLE_SCOPES,
    gdrive_settings=gdrive_settings
)

# Create the GDriveClient instance
gdrive_client = GDriveClient(gdrive_config)

# --- 3. Download a file ---
# Specify the target to download the file
target = DownloadTarget (
  file_id = "some_file_id",
  destination_path = Path("data/destinatio_dir/myfile.csv"),
  mime_type = None
)

print(f"Downloading '{file_name}'...")
gdrive_client.download_file(
  target
)
print(f"File successfully downloaded to '{download_dir}'")
```

### Data Professional Workflow: Load a Google Sheet into Pandas

A common task for data analysts is to pull the latest version of a report from
Google Drive.
This example shows how to find a Google Sheet by its path and load its contents
directly into a pandas DataFrame.

```python
import pandas as pd
from pathlib import Path
from gdrive_suite.drive import GDriveClient, GDriveClientConfig
from gdrive_suite.context import GDriveSettings

# --- Initialization (same as above) ---
CONFIG_DIR = Path("conf/local")
GOOGLE_SCOPES = [
    ["https://www.googleapis.com/auth/drive.readonly, https://www.googleapis.com/auth/drive.file"]
]
gdrive_settings = GDriveSettings(
  config_dir=CONFIG_DIR,
  token_file_name="google_token.json",
  credentials_file_name="google_credentials.json"
)
gdrive_config = GDriveClientConfig(GOOGLE_SCOPES, gdrive_settings)
gdrive_client = GDriveClient(gdrive_config)

# --- Find and load the sheet ---
try:
    # Find the folder ID by navigating from the root ('root')
    # This is more robust than hard coding folder IDs
    folder_path = ["Sales Reports", "2025", "Q3"]
    target_folder_id = gdrive_client.find_folder_id_by_path(
        start_folder_id="root",
        path_segments=folder_path
    )

    if target_folder_id:
        # Now, list files in that folder to find our report
        query = f"'{target_folder_id}' in parents and name='Q3 Sales Summary'"
        files = gdrive_client.list_files(query)

        if files:
            sheet_file = files[0]
            print(f"Found file: {sheet_file['name']} (ID: {sheet_file['id']})")

            # Retrieve the data from the first sheet (tab)
            sheet_data = gdrive_client.retrieve_sheet_data(
                spreadsheet_id=sheet_file['id'],
                sheet_range="Sheet1" # Reads the entire sheet
            )

            if sheet_data:
                # Convert to a pandas DataFrame
                df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
                print("\nSuccessfully loaded data into DataFrame:")
                print(df.head())
            else:
                print("Sheet contains no data.")
        else:
            print("Could not find the specified file in the target folder.")

except (IOError, ValueError) as e:
    print(f"An error occurred: {e}")

```

---

### API Reference

`GDriveClient`
The main class for interacting with Google Drive.

- `download_file(directory_path, file_id, file_name, mime_type=None)`:
  Downloads a file. Use `mime_type` to export Google Workspace files (e.g., `application/pdf`).

- `upload_file(file_path, folder_id, **metadata)`: Uploads a local file to a
  specified folder.

- `retrieve_file_content(file_id)`: Retrieves file content as a `BytesIO`
  object for in-memory use.

- `list_files(query, **list_params)`: Lists files using the standard
  Google Drive API query syntax.

- find_folder_id_by_path(start_folder_id, path_segments): Navigates a path
  to find a folder's ID.

- `retrieve_sheet_data(spreadsheet_id, sheet_range)`: Retrieves data
  |from a Google Sheet.

`GDriveClientConfig`
Handles configuration and authentication.

- `**init**(config_dir_path, scope)`: Initializes the configuration manager.

- `get_credentials()` : Returns valid OAuth2 credentials, handling the
  auth flow and token refreshing.

### Contributing

Contributions are welcome! If you have a feature request, bug report,
or pull request, please open an issue or PR on the [GitHub repository](https://github.com/TheLionCoder/gdrive-suite).

### License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE)
file for details.
