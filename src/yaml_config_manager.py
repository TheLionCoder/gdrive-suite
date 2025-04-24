# *-* encoding: utf-8 *-*
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class YamlConfigManager:
    """
    YamlConfigManager class

    Handles loading and accessing properties from YAML config files.

    Provides a simple interface for loading YAML configuration files
    and accessing nested properties using dot notation or key sequences
    """

    def __init__(self, file_path: Path):
        """Initialize the YAML configuration
        :param file_path: Path to the YAML configuration file_path
        :raises:
            TypeError: If a file path is not a Path object.
            ValueError: If the YAML file cannot be loaded.
        """
        if not isinstance(file_path, Path):
            raise TypeError("file_path must be a Path object")

        self._config_file: Path = file_path
        self._config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Loads the configuration from the config file.
        :return: Dictionary containing the configuration
        :raise:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If there's an error parsing the YAML file.
        """
        if not self._config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self._config_file}"
            )

        try:
            with open(self._config_file, "r") as stream:
                return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ValueError(f"Error while loading config file: {exc}")

    def get_property(self, *keys, default: Optional[Any] = None) -> Any:
        """Get a property from the configuration using a sequence of keys.
           Traverses the configuration dictionary using the provided keys.
        :param default: Value to return if the property is not found.
            If not provided, a ValueError will be raised.
        :return: The requested configuration value.
        :raise:
            ValueError: If the key path does not exist, and no default is provided.
        """
        if not keys:
            return self._config

        value: Dict[str, Any] = self._config

        for key in keys:
            try:
                value = value[key]
            except (KeyError, TypeError):
                if default is not None:
                    return default
                raise ValueError(
                    f"Property not found at path: {'.'.join(str(key) for key in keys)}"
                )
        return value

    def get(self, property_path: str, default: Optional[Any] = None) -> Any:
        """Get a property using a dot notation path.
        :param property_path: Dot-separated path to the property(e.j., "database.host")
        :param default: Value to return if the property is not found.
            If not provided, a ValueError will be raised.
        :return: The requested configuration value.
        """
        keys: List[str] = property_path.split(".")
        return self.get_property(*keys, default=default)

    def reload(self) -> None:
        """Reload the configuration file.
        Useful when the configuration file has been modified.
        :raise ValueError: If there's an error, load the configuration.
        """
        self._config: Dict[str, Any] = self._load_config()
