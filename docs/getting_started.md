# Getting Started

## Installation

Install `gdrive-suite` directly from PyPi. The library requires Python 3.11
or higher.

```bash
pip install gdrive-suite
```

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

````sh

- Place credentials in `conf/local`

```bash
├── conf
│   └── local
│       ├── credentials.json
├── src
│   ├── script.py

````

The first time you run your application, you will be prompted to authorize it via
a browser window. A `google_token.json` file will then be created in the same directory.
This token will be automatically refreshed as needed.
