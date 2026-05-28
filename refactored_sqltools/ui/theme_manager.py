"""
Theme Manager for SQL SysHub.

Gerencia o tema claro/escuro usando qfluentwidgets.
Persiste a preferência no config manager.
Emite signal global themeChanged para componentes reagirem.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from qfluentwidgets import setTheme, Theme, isDarkTheme, qconfig
from refactored_sqltools.config import get_config_manager


class ThemeManager(QObject):
    """Singleton que gerencia o tema da aplicação e emite mudanças."""

    _instance = None
    theme_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = get_config_manager()
        self._init_theme()

    def _init_theme(self):
        saved = self._config.get("Application", "theme_mode", "Light")
        if saved == "Dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)

    def toggle(self):
        if isDarkTheme():
            setTheme(Theme.LIGHT)
            self._config.set("Application", "theme_mode", "Light")
        else:
            setTheme(Theme.DARK)
            self._config.set("Application", "theme_mode", "Dark")
        self.theme_changed.emit()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def toggle_theme(cls):
        cls.get_instance().toggle()
