""" "
gdrive_suite

A python tool designed to work with cloud-based storage services
"""

__version__ = "0.1.0"

from .gdrive_exceptions import (
    GDriveSuiteError,
    GDriveAuthError,
    APIError,
    CredentialsNotFoundError,
)
from .context import GDriveSettings, DownloadTarget

from .drive import GDriveClient
from .drive.gdrive_client_config import GDriveClientConfig, get_drive_client_config

__all__ = [
    "GDriveSuiteError",
    "GDriveAuthError",
    "APIError",
    "CredentialsNotFoundError",
    "GDriveSettings",
    "DownloadTarget",
    "GDriveClientConfig",
    "GDriveClient",
    "get_drive_client_config",
]
