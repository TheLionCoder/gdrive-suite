from dataclasses import dataclass
from pydantic import BaseModel
from pydantic.types import Path
from pydantic.validate_call_decorator import ConfigDict

@dataclass(frozen=True)
class GDriveConfigParams():
    """
    Configuration parameters for Google Drive client.

    Attributes:
        config_dir_path: Path to the configuration directory
          where the token and credentials files are stored.
        token_file_name: The filename for the stored user token.
        credentials_file_name: The filename for the client secret file.
    """
    config_dir_path: Path
    token_file_name: str
    credentials_file_name: str
