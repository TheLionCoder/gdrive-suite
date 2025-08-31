# Usage Examples

## Basic Usage: Download a file

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

## Data Professional Workflow: Load a Google Sheet into Pandas

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
