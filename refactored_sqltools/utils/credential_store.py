"""
Optional secure credential storage helpers.

The app never writes database passwords to settings.ini. If the optional
keyring package is available, passwords are stored in the operating system
credential vault. Without it, the functions fail closed.
"""

from typing import Optional


SERVICE_NAME = "SQLSysHub"


def _get_keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def make_credential_key(db_type: str, host: str, port: str, username: str, database: str) -> str:
    """Build a stable account key for one database connection."""
    parts = [db_type, host, port, username, database]
    return "|".join((part or "").strip() for part in parts)


def save_password(key: str, password: str) -> bool:
    """Save a password to the OS credential store when available."""
    if not key or not password:
        return False

    keyring = _get_keyring()
    if keyring is None:
        return False

    try:
        keyring.set_password(SERVICE_NAME, key, password)
        return True
    except Exception:
        return False


def load_password(key: str) -> Optional[str]:
    """Load a password from the OS credential store when available."""
    if not key:
        return None

    keyring = _get_keyring()
    if keyring is None:
        return None

    try:
        return keyring.get_password(SERVICE_NAME, key)
    except Exception:
        return None
