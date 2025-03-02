# :snake: Cloud Utils

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Python tool designed to work with cloud-based storage services
(Google Drive only supported currently) providing.

---

## :box: Installation

```bash
cd my-python-project
git submodule add git@github.com:TheLionCoder/cloud-utils.git src/cloud_utils
```

---

## :hammer_and_wrench: Usage

### Initial Setup

- Create a configuration directory (recommended):

```bash
mkdir -p conf/local
```

- Place credentials in `conf/local`

```bash
├── conf
│   └── local
│       ├── credentials.json
├── src
│   ├── mde.py
│   ├── cloud_utils
│   │   ├── README.md
│   │   ├── hello.py
│   │   ├── pyproject.toml
│   │   ├── src
│   │   │   ├── gdrive_client.py
│   │   │   ├── gdrive_client_config.py
│   │   │   └── yaml_config_manager.py
│   │   └── uv.lock
```

### Basic Implementation

```python
# project/src/mde.py
from src.cloud_utils.src.gdrive_client import GdriveClient
from mde_analysis_project.cloud_utils.src.gdrive_client_config import GDriveClientConfig
from mde_analysis_project.cloud_utils.src.yaml_config_manager import YamlConfigManager

if __name__ == "__main__":
    PROJ_ROOT = Path(__file__).resolve().parents[1]
    CONFIG_DIR = PROJ_ROOT / "conf" / "local"
    google_scope: List[str]: ["https://www.googleapis.com/auth/drive.readonly",
                              "https://www.googleapis.com/auth/drive.file"]

    config_drive = GDriveClientConfig(
        config_dir_path=CONFIG_DIR, scope=google_scope
    )
    gdrive_client: GDriveClient = GDriveClient(config_drive)

    # Download and excel file
    gdrive_client.download_file(
        directory_path=".", file_id="123id", file_name="mde.xlsx", mime_type=None
    )
```

---

## :key: Configuration Notes

- Ensure credentials.json contain valid keys
- Scope defines application permissions(read-only/file access shown)
- MIME type can be specified for explicit file conversion
