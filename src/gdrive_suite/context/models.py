from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GDriveSettings:
    """
    Configuration parameters for Google Drive client.

    Attributes:
        config_dir_path: Path to the configuration directory where the token and credentials files are stored.
        token_file_name: The filename for the stored user token.
        credentials_file_name: The filename for the client secret file.
    """

    config_dir_path: Path
    token_file_name: str
    credentials_file_name: str


@dataclass(frozen=True)
class DownloadTarget:
    """
    Specifies the parameters for a file download operation

    Attributes:
        file_id: The unique ID of the file on Google Drive.
        destination_path: The full local path(including filename) wjere
            file will be saved.
        mime_type: An optional MIME type to convert a Google Workspace
            to a different format upon download (e.g., 'application/pdf').
    """

    file_id: str
    destination_path: Path
    mime_type: Optional[str]
