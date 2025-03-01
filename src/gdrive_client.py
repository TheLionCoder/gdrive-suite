import io
from pathlib import Path
from typing import Any, Dict, List, Optional


from gdrive_client_config import GDriveClientConfig
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


class GDriveClient:
    """
    Provides functionality to:
    - Download files from Google Drive with or without conversion
    - Upload files to Google Drive
    - Retrieve Google Sheets data
    """

    def __init__(self, drive_config_manager):
        """Initializes the GdriveService
        :param drive_config_manager: A ConfigManager that provides OAuth2 credentials.
        """
        self._credentials: GDriveClientConfig = drive_config_manager.get_credentials()
        self._services: Dict[str, Any] = {
            "drive": build(
                serviceName="drive", version="v3", credentials=self._credentials
            ),
            "sheets": build(
                serviceName="sheet", version="v4", credentials=self._credentials
            ),
        }

    @property
    def creds(self):
        """Get the OAuth2 credentials"""
        return self._credentials

    @property
    def drive_service(self):
        """Get the Google Drive service"""
        return self._services["drive"]

    @property
    def sheets_service(self):
        """Get the Google Sheets service."""
        return self._services["sheets"]

    def download_file(
        self,
        directory_path: Path,
        file_id: str,
        file_name: str,
        mime_type: Optional[str] = None,
    ) -> None:
        """Download a file from Google Drive.
        :param directory_path: Directory to save the file to download
        :param file_id: Google ID of the file to download
        :param mime_type: Optional MIME type for export (for Google Workspace files).
                       See: https://developers.google.com/drive/api/guides/ref-export-formats
        :raise
            Exception if the download fails
        """
        file_path: Path = directory_path.joinpath(file_name)

        try:
            # Get the appropiate request based on mime_type
            if mime_type:
                request = self.drive_service.files().export_media(
                    fileId=file_id, mimeType=mime_type
                )
            else:
                request = self.drive_service.files().get_media(fileId=file_id)

            # Execute the download
            with open(file_path, "wb") as file_writer:
                downloader: MediaIoBaseDownload = MediaIoBaseDownload(
                    fd=file_writer, request=request
                )
                self._execute_download(downloader)

        except Exception as e:
            raise Exception(f"Failed to download {file_id}: {str(e)}")

    def _execute_download(self, downloader: MediaIoBaseDownload) -> None:
        """Execute a download operation with progress track
        :param downloader: MediaIoBaseDownload instance
        """
        done: bool = False
        # Make a loop to get the (status and done)
        while not done:
            _, done = downloader.next_chunk()

    def retrieve_file_content(self, file_id: str) -> io.BytesIO:
        """Retrieve a file from Google Drive as BytesIO object
        :param file_id: Google ID of the file to get retrieve_file_content
        :return: BytesIO object containing the file content
        :raises:
            Exception: if retrieval fails
        """
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_content: io.BytesIO = io.BytesIO()
            downloader: MediaIoBaseDownload = MediaIoBaseDownload(
                fd=file_content, request=request
            )

            self._execute_download(downloader)
            file_content.seek(0)
            return file_content

        except Exception as e:
            raise Exception(f"Failed to retrieve file content for {file_id}: {str(e)}")

    def retrieve_sheet_data(self, file_id: str, sheet_range: str) -> List[List[Any]]:
        """Read data from a google sheet
        :param file_id: ID for the google sheet
        :param sheet range: Range of cells to read (e.j., A1:Z90)
        :return: List of rows containing cell values
        """
        try:
            result = (
                self.sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=file_id, range=sheet_range)
                .execute()
            )
            return result.get("values", [])

        except Exception as e:
            raise Exception(
                f"Failed to retrieve sheet data from file: {file_id}: {str(e)}"
            )

    def upload_file(
        self, file_path: str, file_name: str, folder_id: str, mime_type: str, **metadata
    ) -> str:
        """Upload file to Google Drive
        :param file_path: Path to the file to the upload
        :param file_name: Name for the uploaded file
        :param folder_id: ID of the folder to upload to
        :param mime_type: MIME type of the file
        :metadata: Additional metadata to add the file
        """
        try:
            file_metadata = {"name": file_name, "parents": [folder_id], **metadata}
            media: MediaFileUpload = MediaFileUpload(
                filename=file_name, mimetype=mime_type, resumable=True
            )
            response = (
                self.drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            return response.get("id")
        except Exception as e:
            raise Exception(f"Failed to upload file {file_path}: {str(e)}")
