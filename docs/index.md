# Gdrive-Suite

GDrive Suite is a robust Python library designed to streamline interaction with Google Drive and Google Sheets. It provides an intuitive, high-level interface over the official Google APIs, handling authentication, token management, and API calls so you can focus on your data workflows.

Whether you're a data engineer building ETL pipelines, a data analyst fetching the latest reports, or a data scientist accessing datasets, GDrive Suite simplifies cloud file management.

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
