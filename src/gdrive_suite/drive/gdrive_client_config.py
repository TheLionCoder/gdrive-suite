"""
Handles credential management for Google Drive API access.
"""

import functools
from pathlib import Path
from typing import Optional, List, Tuple, Union, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.credentials import Credentials as BaseCredentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from loguru import logger
import google.auth

from gdrive_suite import (
    ConfigDirectoryError,
    CredentialsNotFoundError,
    GDriveAuthError,
    GDriveSettings,
)

CredentialsTypes = Union[BaseCredentials, Credentials]


class GDriveClientConfig:
    """
    Handles credential management including retrieving, refreshing, and
    storing oauth2 credentials for Google Drive API access, both local file
    based and default application credentials found in a server environment.
    """

    def __init__(self, scopes: List[str], gdrive_settings: GDriveSettings):
        """Constructor for the GoogleDriveClientConfig

        Args:
            scopes: A list of OAuth2 scopers required for the application.
            gdrive_settings: The configuration parameters for the Google Drive client.
        Raises:
            ConfigDirectoryError: If config_dir_path is not a valid directory.
        """
        self.scopes: List[str] = scopes
        try:
            gdrive_settings.config_dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ConfigDirectoryError(
                f"Error accessing or creating config directory '{gdrive_settings.config_dir_path}': {e}"
            ) from e

        self.token_file_path: Path = (
            gdrive_settings.config_dir_path / gdrive_settings.token_file_name
        )
        self.credential_file_path: Path = (
            gdrive_settings.config_dir_path / gdrive_settings.credentials_file_name
        )

    def _get_default_credentials(self) -> Optional[Credentials]:
        """
        Tries to get credentials from the application default environment.
        This is the method used in server environments like Cloud functions.
        """
        try:
            creds, _ = google.auth.default(scopes=self.scopes)
            if isinstance(creds, Credentials):
                logger.opt(colors=True).success(
                    "Using Application Default Credentials."
                )
                return creds
        except DefaultCredentialsError:
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

        logger.opt(colors=True).info(
            "No default credentials. Attempting to load credentials from local files."
        )

        creds = self._load_local_token()

        if creds and creds.expired:
            logger.opt(colors=True).success(
                "Successfully loaded and validated local credentials."
            )
            return creds

        # If we have valid creds, return them
        if creds and creds.valid:
            logger.opt(colors=True).success(
                "Successfully loaded and validated local credentials."
            )
            return creds

        logger.opt(colors=True).info("No valid token. Starting new OAuth2 flow.")
        creds = self._run_oauth_flow()
        if creds:
            return creds
        raise CredentialsNotFoundError(
            "Failed to obtain credentials. Ensure ´google_credentials.json´"
            " exists for local flow or that ADC are configured on the server."
        )

    def _load_local_token(self) -> Optional[Credentials]:
        """Load credentials from the file toke if it exists.
        Returns:
            Credentials object if a token file exists, None otherwise
        """
        if self.token_file_path.exists():
            try:
                return Credentials.from_authorized_user_file(
                    str(self.token_file_path), self.scopes
                )
            except Exception as e:
                logger.opt(colors=True).warning(
                    f"Could not load token from {self.token_file_path}: {e}"
                )
        return None

    def _save_local_token(self, creds: Credentials) -> None:
        """Save credentials to the token file"""
        try:
            with open(self.token_file_path, "w") as token_file:
                token_file.write(creds.to_json())
            self.token_file_path.chmod(0o600)
        except (OSError, IOError) as e:
            raise GDriveAuthError(f"Could not write token file {e}")

    def _refresh_credentials(self, creds: Credentials) -> Optional[Credentials]:
        """Refreshes expired credentials and saves the new token."""
        logger.opt(colors=True).info(
            "Credentials expired. Attempting to refresh token."
        )
        try:
            creds.refresh(Request())
            logger.opt(colors=True).success("Successfully refreshed credentials.")
            return creds
        except RefreshError as e:
            logger.opt(colors=True).error(
                f"Token refresh failed: {e}. A new login is required."
            )
            if self.token_file_path.exists():
                self.token_file_path.unlink()
            return None

    def _run_oauth_flow(self) -> Optional[Credentials]:
        """
        Runs the interactive OAuth2 flow to obtain new credentials.
        """
        if not self.credential_file_path.exists():
            logger.opt(colors=True).warning(
                f"Cannot start OAuth flow: secrets file not found at '{self.credential_file_path}"
            )
            return None

        try:
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=str(self.credential_file_path), scopes=self.scopes
            )
            creds_from_flow: Optional[CredentialsTypes] = flow.run_local_server(port=0)

            if isinstance(creds_from_flow, Credentials):
                creds = cast(Credentials, creds_from_flow)
                self._save_local_token(creds)
                logger.opt(colors=True).success(
                    "Successfully obtained new credentials via OAuth2 flow."
                )
                return creds
            else:
                logger.opt(colors=True).error(
                    f"OAuth2 flow returned and unexpected credential type: {type(creds_from_flow)}"
                )
                return None

        except Exception as e:
            logger.opt(colors=True).error(
                f"An error ocurred during the OAuth2 flow: {e}"
            )
            return None


def get_drive_client_config(
    scopes: List[str], gdrive_settings: GDriveSettings
) -> GDriveClientConfig:
    """
    Returns a cached, singleton-like instance of the GDriveClientConfig.
    """
    frozen_scopes: Tuple[str, ...] = tuple(sorted(scopes))
    return _get_config(frozen_scopes, gdrive_settings)


@functools.lru_cache(maxsize=None)
def _get_config(
    scopes_tuple: Tuple[str, ...], gdrive_settings: GDriveSettings
) -> GDriveClientConfig:
    return GDriveClientConfig(list(scopes_tuple), gdrive_settings)
