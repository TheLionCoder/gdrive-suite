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
        """
        self.scopes: List[str] = scopes
        self.token_file_path: Path = (
            gdrive_settings.config_dir_path / gdrive_settings.token_file_name
        )
        self.credential_file_path: Path = (
            gdrive_settings.config_dir_path / gdrive_settings.credentials_file_name
        )

    def get_credentials(self) -> Optional[Credentials]:
        """
        Retrieves valid Google API credetials using a prioritized strategy.

        Returns:
            A valid 'google.oauth2.credentials.Credentials' object.

        Raises:
            CredentialsNotFoundError: If no credentials can be found or
                generated through any of the available methods.
        """
        creds: Optional[Credentials] = self._get_default_credentials()
        if creds:
            return creds

        logger.opt(colors=True).info(
            "No default credentials. Attempting to load credentials from local files."
        )

        creds = self._get_local_credentials()
        if creds:
            return creds

        raise CredentialsNotFoundError(
            "Failed to obtain credentials. For local execution, ensure "
            f"'{self.credential_file_path.name}' is in '{self.credential_file_path.parent}.'"
            "For server execution, ensure Application Default Credentials are configured."
        )

    def _get_local_credentials(self) -> Optional[Credentials]:
        """
        Manages the entire lifecycle of local, file-baed credentials.

        It attempts to load, validate, and refresh and existing token.
        If that fails, it initiates a new OAuth2 flow.
        Load credentials from the file toke if it exists.
        Returns:
            Credentials object if a token file exists, None otherwise
        """
        creds = self._load_local_token()

        if creds:
            if creds.valid:
                logger.opt(colors=True).success(
                    "Successfully loaded a valid local credentials."
                )
                return creds
            if creds.expired and creds.refresh_token:
                refreshed_creds = self._refresh_credentials(creds)
                if refreshed_creds:
                    self._save_local_token(refreshed_creds)
                    return refreshed_creds

        logger.opt(colors=True).warning(
            "No valid token found. Starting new OAuth2 flow."
        )
        new_creds = self._run_oauth_flow()
        if new_creds:
            self._save_local_token(new_creds)
            return new_creds

        return None

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

    def _load_local_token(self) -> Optional[Credentials]:
        """
        Manages the entire lifecycle of local, file-based credentials.

        It attempts to load, validate, and refresh and existing token.
        If that fails, it initiates a new OAuth2 flow.
        Load credentials from the file toke if it exists.
        Returns:
            Credentials object if a token file exists, None otherwise
        """

        if not self.token_file_path.exists():
            return None
        try:
            return Credentials.from_authorized_user_file(
                str(self.token_file_path), self.scopes
            )
        except Exception as err:
            logger.opt(colors=True).warning(
                f"Could not load token from '{self.token_file_path}': {err}"
            )
            return None

    def _save_local_token(self, creds: Credentials) -> None:
        """Save credentials to the token file with secure permissions."""
        try:
            logger.opt(colors=True).info(
                f"Saving credentials to '{self.token_file_path}'"
            )
            self.token_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_file_path.write_text(creds.to_json())
            self.token_file_path.chmod(0o600)
        except (OSError, IOError) as err:
            raise GDriveAuthError(f"Could not write token file {err}")

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
                str(self.credential_file_path), self.scopes
            )
            creds_from_flow: Optional[CredentialsTypes] = flow.run_local_server(port=0)

            if isinstance(creds_from_flow, Credentials):
                creds = cast(Credentials, creds_from_flow)
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
    scopes: List[str], gdrive_settings: Optional[GDriveSettings]
) -> GDriveClientConfig:
    """
    Acts as a factory to get a cached, singleton-like instance of the
    GDriveClientConfig for a given set of scopes and settings.

    This prevents re-creating the configuration unnecessarily.

    Args:
        scopes: List of OAuth2 scopres.
        gdrive_settings: Optional GDriveSettings. If None, default
            paths in the user's home directory are used.
    """
    if not gdrive_settings:
        gdrive_settings = GDriveSettings(
            config_dir_path=Path.home() / ".gdrive_suite/",
            token_file_name="token.json",
            credentials_file_name="credentials.json",
        )

    frozen_scopes: Tuple[str, ...] = tuple(sorted(scopes))
    return _get_cached_config(frozen_scopes, gdrive_settings)


@functools.lru_cache(maxsize=None)
def _get_cached_config(
    scopes_tuple: Tuple[str, ...], gdrive_settings: GDriveSettings
) -> GDriveClientConfig:
    """Cached internal function to create the config object."""
    return GDriveClientConfig(list(scopes_tuple), gdrive_settings)
