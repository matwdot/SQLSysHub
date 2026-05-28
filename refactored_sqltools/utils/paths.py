"""
Path helpers for development and packaged execution.
"""

import os
import sys
from pathlib import Path


APP_NAME = "SQLSysHub"


def get_base_path() -> Path:
    """Return the read-only application base path."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def get_user_data_path() -> Path:
    """Return a writable user data directory."""
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    path = root / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_user_config_path() -> Path:
    """Return a writable user configuration file path."""
    return get_user_data_path() / "settings.ini"


def resolve_asset_path(*parts: str) -> Path:
    """Resolve an application asset path."""
    return get_base_path().joinpath(*parts)
