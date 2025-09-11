"""
Custom exception for the gdrive_suite package.

This module defines a hierarchy of custon exceptions to allow for specific
error handling when interacting with the Google Drive and Sheets API.
"""


class GDriveSuiteError(Exception):
    """Base Exception for all errors rised by the gdrive-suite library."""

    pass


class GDriveAuthError(Exception):
    """Base exception for authentication errors in this module."""

    pass


class CredentialsNotFoundError(GDriveAuthError):
    """Raised when no valid credentials can be found or generated."""

    pass


class APIError(GDriveSuiteError):
    """Raised when an API call to a Google service fails.

    This exception abstracts away the underlying 'googleapiclient.http.HttpError'
    providing a consisteng error type for all API interactions within the suite.
    """

    pass
