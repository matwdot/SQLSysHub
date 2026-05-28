"""
Configuration manager.

Stores non-sensitive user preferences in an INI file. Database passwords are
intentionally excluded and must be handled by a secure credential store.
"""

import configparser
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from refactored_sqltools.utils.paths import get_user_config_path as _get_user_config_path


logger = logging.getLogger(__name__)


def get_user_config_path() -> Path:
    """Return the writable user configuration path."""
    return _get_user_config_path()


class ConfigManager:
    """System configuration manager."""

    DEFAULT_CONFIG = {
        "Connection": {
            "db_type": "Firebird",
            "host": "localhost",
            "port": "3050",
            "username": "SYSDBA",
            "database_option": "SRV",
            "custom_database": "",
        },
        "Application": {
            "last_operation": "",
            "theme": "Fusion",
            "theme_mode": "Light",
            "remember_connection": "true",
            "auto_connect": "false",
        },
        "Window": {
            "width": "1200",
            "height": "800",
            "x": "100",
            "y": "100",
            "maximized": "false",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else get_user_config_path()
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self):
        """Load configuration from disk, applying safe defaults first."""
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)

        if self.config_path.exists():
            try:
                self.config.read(self.config_path, encoding="utf-8")
                if self.config.has_option("Connection", "password"):
                    self.config.remove_option("Connection", "password")
                    self._save_config()
                logger.info("Configuracoes carregadas de: %s", self.config_path)
            except Exception as exc:
                logger.warning("Erro ao carregar configuracoes: %s", exc)
        else:
            self._save_config()
            logger.info("Arquivo de configuracao criado: %s", self.config_path)

    def _save_config(self):
        """Save configuration atomically."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            if self.config.has_option("Connection", "password"):
                self.config.remove_option("Connection", "password")

            temp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
            with open(temp_path, "w", encoding="utf-8") as file:
                self.config.write(file)
            temp_path.replace(self.config_path)
            logger.debug("Configuracoes salvas em: %s", self.config_path)
        except PermissionError:
            logger.error("Sem permissao para salvar em: %s", self.config_path)
        except Exception as exc:
            logger.error("Erro ao salvar configuracoes: %s", exc)

    def get_config_path(self) -> str:
        return str(self.config_path)

    def get_connection_config(self) -> Dict[str, str]:
        return {
            "db_type": self.config.get("Connection", "db_type"),
            "host": self.config.get("Connection", "host"),
            "port": self.config.get("Connection", "port"),
            "username": self.config.get("Connection", "username"),
            "database_option": self.config.get("Connection", "database_option"),
            "custom_database": self.config.get("Connection", "custom_database"),
        }

    def save_connection_config(
        self,
        db_type: str,
        host: str,
        port: str,
        username: str,
        database_option: str,
        custom_database: str = "",
    ):
        """Save non-sensitive connection settings."""
        self.config.set("Connection", "db_type", db_type)
        self.config.set("Connection", "host", host)
        self.config.set("Connection", "port", port)
        self.config.set("Connection", "username", username)
        self.config.set("Connection", "database_option", database_option)
        self.config.set("Connection", "custom_database", custom_database)
        self._save_config()
        logger.info("Configuracoes de conexao salvas")

    def get_last_operation(self) -> str:
        return self.config.get("Application", "last_operation")

    def set_last_operation(self, operation: str):
        self.config.set("Application", "last_operation", operation)
        self._save_config()

    def get_theme(self) -> str:
        return self.config.get("Application", "theme")

    def set_theme(self, theme: str):
        self.config.set("Application", "theme", theme)
        self._save_config()

    def should_remember_connection(self) -> bool:
        return self.config.getboolean("Application", "remember_connection")

    def set_remember_connection(self, remember: bool):
        self.config.set("Application", "remember_connection", str(remember).lower())
        self._save_config()

    def should_auto_connect(self) -> bool:
        return self.config.getboolean("Application", "auto_connect")

    def set_auto_connect(self, auto_connect: bool):
        self.config.set("Application", "auto_connect", str(auto_connect).lower())
        self._save_config()

    def get_window_geometry(self) -> Dict[str, Any]:
        return {
            "width": self.config.getint("Window", "width"),
            "height": self.config.getint("Window", "height"),
            "x": self.config.getint("Window", "x"),
            "y": self.config.getint("Window", "y"),
            "maximized": self.config.getboolean("Window", "maximized"),
        }

    def save_window_geometry(self, width: int, height: int, x: int, y: int, maximized: bool):
        self.config.set("Window", "width", str(width))
        self.config.set("Window", "height", str(height))
        self.config.set("Window", "x", str(x))
        self.config.set("Window", "y", str(y))
        self.config.set("Window", "maximized", str(maximized).lower())
        self._save_config()

    def get(self, section: str, key: str, fallback: str = "") -> str:
        return self.config.get(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self._save_config()


_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Return the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
