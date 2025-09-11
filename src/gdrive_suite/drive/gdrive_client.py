import io
from pathlib import Path
from typing import Any, List, Optional, Dict

from google.oauth2.credentials import Credentials
from .gdrive_client_config import GDriveClientConfig
from googleapiclient.discovery import build
from googleapiclient.http import HttpError, MediaIoBaseDownload, MediaFileUpload
from google.auth.exceptions import RefreshError
from loguru import logger

from gdrive_suite import APIError, GDriveAuthError, DownloadTarget


def _execute_download(downloader: MediaIoBaseDownload) -> None:
    """Execute a download operation with progress track

    Args:
       downloader: MediaIoBaseDownload instance
    """
    done: bool = False
    # Make a loop to get the (status and done)
    while not done:
        _, done = downloader.next_chunk()


class GDriveClient:
    """
    Provides functionality to:
    - Download files from Google Drive with or without conversion
    - Upload files to Google Drive
    - Retrieve Google Sheets data
    """

    def __init__(self, drive_config_manager: GDriveClientConfig):
        """Initializes the GdriveService
        :param drive_config_manager: A ConfigManager that provides
         Outh2 credentials.
        """
        try:
            self._credentials: Optional[Credentials] = (
                drive_config_manager.get_credentials()
            )
            self.drive_service: Any = build(
                "drive", version="v3", credentials=self._credentials
            )
            self._sheets_service: Any = build(
                serviceName="sheets", version="v4", credentials=self._credentials
            )

        except RefreshError as e:
            raise GDriveAuthError(
                f"Failed to refres credentials. please re-authenticate. Details: {e}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google API services: {e}") from e

    def download_file(self, target: DownloadTarget) -> None:
        """Download a file from Google Drive.

        Args:
            target: A `DownloadTarget` object specifyng what a download and
                where to save it.
        Raises:
            APIError: If the download fails due to a Google API error.
            IOError: For local file system errors.
        """
        if target.destination_path.parent:
            target.destination_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            request = (
                self.drive_service.files().export_media(
                    fileId=target.file_id, mimeType=target.mime_type
                )
                if target.mime_type
                else self.drive_service.files().get_media(fileId=target.file_id)
            )
            with open(target.destination_path, "wb") as file_writer:
                downloader: MediaIoBaseDownload = MediaIoBaseDownload(
                    fd=file_writer, request=request
                )
                _execute_download(downloader)

        except HttpError as e:
            raise APIError(
                f"Failed to download file '{target.destination_path.name}' (ID: {target.file_id})."
                f"Reason: {e.resp.status} {e.resp.reason}"
            ) from e
        except IOError as e:
            raise IOError(
                f"An expected error ocurred while downloading '{target.destination_path.name}': {e}"
            ) from e

    def retrieve_file_content(self, file_id: str) -> io.BytesIO:
        """Retrieve a file from Google Drive as BytesIO object
        Args
         file_id: Google ID of the file to get retrieve_file_content.

         Return:
         BytesIO object containing the file content

         Raises:
           APIError: If the retrieve fails due to Google API error.
           IOError: For local file system errors.
        """
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_content: io.BytesIO = io.BytesIO()
            downloader: MediaIoBaseDownload = MediaIoBaseDownload(
                fd=file_content, request=request
            )

            _execute_download(downloader)
            file_content.seek(0)
            return file_content

        except HttpError as e:
            raise APIError(
                f"Failed to retrieve file content for '{file_id}'. "
                f"Reason: {e.resp.status} {e.resp.reason}"
            ) from e
        except IOError as e:
            raise IOError(
                f"An unexpected error ocurred while retrieving content "
                f"for file ID: '{file_id}': {e}"
            )

    def retrieve_sheet_data(
        self, spreadsheet_id: str, sheet_range: str
    ) -> List[List[Any]]:
        """Read data from a Google sheet
        Args:
             spreadsheet_id: ID for the Google sheet
             sheet_range: Range of cells to read (e.j., A1: Z90)

        Returns:
            List of rows containing cell values

        Raises:
            APIError: If retrieving data fails due to a Google API error.
        """
        try:
            result = (
                self._sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=sheet_range)
                .execute()
            )
            return result.get("values", [])

        except HttpError as e:
            raise APIError(
                f"Failed to retrieve data from sheet '{spreadsheet_id}'. "
                f"Reason: {e.resp.status} {e.resp.reason}"
            ) from e

    def upload_file(self, file_path: Path, folder_id: str, **metadata: Any) -> str:
        """Upload file to Google Drive

        Args:
             file_path: Path to the file to the upload
             folder_id: ID of the folder to upload to
             metadata: Additional metadata to add the file

        Raises:
            APIError: If upload fails due to Google API error.
            IOError: For local file system errors.
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"The specific file does not exist: {file_path}")

        try:
            file_metadata = {"name": file_path.name, "parents": [folder_id], **metadata}
            media: MediaFileUpload = MediaFileUpload(str(file_path), resumable=True)
            response = (
                self.drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            return response.get("id")
        except HttpError as e:
            raise APIError(
                f"Failed to upload file {file_path.name}. "
                f"Reason: {e.resp.status} {e.reason}"
            ) from e
        except IOError as e:
            raise IOError(
                f"An unexpected error ocurred during the upload "
                f"of '{file_path.name}': {e}"
            ) from e

    def list_files(self, query: str, **list_params: Any) -> List[Dict[str, Any]]:
        """Helper function to list files in Google Drive
        Args:
         query: A query for filtering results. See "Search for files"
         guide for support syntax.
         list_params: Additional parameters for listing files.
         Return:
         List of searches files.

         Raises:
           APIError: If the list files fails due to Google API error.
        """
        all_files: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        try:
            while True:
                response: Any = (
                    self.drive_service.files()
                    .list(
                        spaces="drive",
                        q=query,
                        pageToken=page_token,
                        corpora="user",
                        fields="nextPageToken, files(id, name, parents, mime)",
                        **list_params,
                    )
                    .execute()
                )
                all_files.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)

                if page_token is None:
                    break
            return all_files
        except HttpError as e:
            raise APIError(
                f"Failed to list files with query '{query}'. "
                f"HTTP Error: {e.resp.status} {e.resp.reason}"
            )

    def find_folder_id_by_path(
        self, start_folder_id: str, path_segments: List[str]
    ) -> Optional[str]:
        """
        Find a folder's ID by navigating a path of folder names.
        Args:
            start_folder_id: The ID of the folder to start from.
            path_segments: A list of folder names to navigate.
        Return:
          The ID of the folder.
        """
        current_folder_id: str = start_folder_id
        for segment in path_segments:
            query: str = f"'{current_folder_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and "
            f"name='{segment}' and trashed=false"
            items = self.list_files(query)
            if not items:
                logger.opt(colors=True).error(
                    f"Could not find folder '{segment}' within "
                    f"parent ID '{current_folder_id}'"
                )
                return None
            current_folder_id = items[0]["id"]
            logger.opt(colors=True).info(
                f"Found folder segment '{{}}' with ID: '{current_folder_id}'"
            )

        return current_folder_id
