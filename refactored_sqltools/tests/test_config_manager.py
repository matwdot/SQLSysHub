import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401

from refactored_sqltools.config.config_manager import ConfigManager


class ConfigManagerTests(unittest.TestCase):
    def test_config_manager_does_not_persist_password(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "settings.ini"
            manager = ConfigManager(str(config_path))

            manager.config.set("Connection", "password", "secret")
            manager.save_connection_config(
                db_type="Firebird",
                host="localhost",
                port="3050",
                username="SYSDBA",
                database_option="SRV",
            )

            content = config_path.read_text(encoding="utf-8")
            self.assertNotIn("password", content.lower())
            self.assertNotIn("secret", content)
            self.assertNotIn("password", manager.get_connection_config())
