from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import DefaultCredentialsError
from loguru import logger
import google.auth


def _refresh_credentials(creds: Credentials) -> Credentials:
    """Refresh expired credentials
    :param creds:  with a valid refresh token
    """
    creds.refresh(Request())
    return creds


class GDriveClientConfig:
    """
    Handles credential management including retrieving, refreshing, and
    storing oauth2 credentials for Google Drive API access, both local file
    based and default application credentials found in a server environment.
    """

    def __init__(
        self,
        config_dir_path: Path,
        scope: list,
    ):
        """Constructor for the GoogleDriveClientConfig
        :param config_dir_path: Path to the configuration directory
         where the token and credentials files are stored.
        :param scope: Scope of the token.
        :raise:
            AssertionError: If config_dir_path is not a directory.
        """
        if not config_dir_path.is_dir():
            raise TypeError("config_dir_path must be a directory")

        self._conf_path: Path = config_dir_path
        self._token_file_path: Path = self._conf_path / "google_token.json"
        self._credential_file_path: Path = self._conf_path / "google_credentials.json"
        self._scope = scope

    def __str__(self):
        """String representation of the GoogleDriveClientConfig"""
        return (
            f"GoogleDriveClientConfig(token_file={self._token_file_path},"
            f"credential_file={self._credential_file_path}, "
            f"scope={self._scope}"
        )

    def _get_default_credentials(self) -> Optional[Credentials]:
        """
        Tries to get credentials from the application default environment.
        This is the method used in server environments like Cloud functions.
        """
        try:
            creds, _ = google.auth.default(scopes=self._scope)
            if creds:
                logger.opt(colors=True).info(
                    "Successfully loaded defauls aplication credentials."
                )
                return creds
        except DefaultCredentialsError:
            logger.opt(colors=True).info(
                "No defauls credentials found. Falling back to local auth flow."
            )
            return None
        return None

    def get_credentials(self) -> Optional[Credentials]:
        """Get valid Oauth2 credentials for Google AI access.

        Attempts to load existing credentials, refresh them if expired,
        or get new ones through the Oauth flow if necessary.

        :return: Valid Google Oauth2 credentials
        """
        creds: Optional[Credentials] = self._get_default_credentials()
        if creds:
            return creds

        logger.opt(colors=True).info("Attempting to load credentials from local files.")
        creds = self._load_existing_credentials()
        # If we have valid creds, return them
        if creds and creds.valid:
            return creds

        # If creds exist but are expired, refresh the token
        if creds and creds.expired and creds.refresh_token:
            creds = _refresh_credentials(creds)
            self._save_credentials(creds)
            return creds
        return None

        return self._get_credentials_from_flow()

    def _load_existing_credentials(self) -> Optional[Credentials]:
        """Load credentials from the file toke if it exists.
        return: Credentials object if a token file exists, None otherwise
        """
        if self._token_file_path.exists():
            return Credentials.from_authorized_user_file(
                filename=str(self._token_file_path), scopes=self._scope
            )
        return None

    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to the token file
        :param creds: Credentials to save
        """
        with open(self._token_file_path, "w") as token_file:
            token_file.write(creds.to_json())

    def _get_credentials_from_flow(self) -> Credentials:
        """Obtain new credentials using Oauth flow
        :return: New credentials obtained through user authorization.
        """
        flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=str(self._credential_file_path), scopes=self._scope
        )
        creds = flow.run_local_server(port=0)
        self._save_credentials(creds)
        return creds
