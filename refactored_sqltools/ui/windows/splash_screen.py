"""
Splash Screen - Tela de Carregamento com Fluent Design.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QFrame, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread

from PyQt5.QtGui import QPixmap

from qfluentwidgets import ProgressBar, CaptionLabel, TitleLabel, BodyLabel, isDarkTheme


class CheckItem(QFrame):
    """Widget para exibir um item de verificação."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(8)

        self.icon_label = QLabel("○")
        self.icon_label.setFixedWidth(18)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = BodyLabel(self.text)

        self.status_label = CaptionLabel("")
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setMinimumWidth(100)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.status_label)

        self._apply_style("pending")

    def _apply_style(self, state):
        dark = isDarkTheme()
        if state == "running":
            self.icon_label.setText("●")
            self.icon_label.setStyleSheet(f"color: {'#60a5fa' if dark else '#3498db'}; font-size: 11px;")
            self.text_label.setStyleSheet(f"color: {'#60a5fa' if dark else '#3498db'}; font-weight: bold;")
            self.status_label.setStyleSheet(f"color: {'#60a5fa' if dark else '#3498db'};")
        elif state == "success":
            self.icon_label.setText("✓")
            self.icon_label.setStyleSheet(f"color: {'#4ade80' if dark else '#27ae60'}; font-size: 11px; font-weight: bold;")
            self.text_label.setStyleSheet(f"color: {'#e2e8f0' if dark else '#2c3e50'};")
            self.status_label.setStyleSheet(f"color: {'#4ade80' if dark else '#27ae60'};")
        elif state == "error":
            self.icon_label.setText("✗")
            self.icon_label.setStyleSheet(f"color: {'#f87171' if dark else '#e74c3c'}; font-size: 11px; font-weight: bold;")
            self.text_label.setStyleSheet(f"color: {'#f87171' if dark else '#e74c3c'};")
            self.status_label.setStyleSheet(f"color: {'#f87171' if dark else '#e74c3c'};")
        elif state == "warning":
            self.icon_label.setText("!")
            self.icon_label.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'}; font-size: 11px; font-weight: bold;")
            self.text_label.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'};")
            self.status_label.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'};")
        else:
            self.icon_label.setText("○")
            self.icon_label.setStyleSheet(f"color: {'#64748b' if dark else '#bdc3c7'}; font-size: 11px;")
            self.text_label.setStyleSheet(f"color: {'#94a3b8' if dark else '#7f8c8d'};")
            self.status_label.setStyleSheet("")

    def set_running(self, message: str = ""):
        self._apply_style("running")
        self.status_label.setText(message)
        QApplication.processEvents()

    def set_success(self, message: str = ""):
        self._apply_style("success")
        self.status_label.setText(message)
        QApplication.processEvents()

    def set_error(self, message: str = ""):
        self._apply_style("error")
        self.status_label.setText(message)
        QApplication.processEvents()

    def set_warning(self, message: str = ""):
        self._apply_style("warning")
        self.status_label.setText(message)
        QApplication.processEvents()


class LoadingWorker(QThread):
    """Worker thread para executar verificações em background."""

    check_started = pyqtSignal(str)
    check_progress = pyqtSignal(str, str)
    check_completed = pyqtSignal(str, bool, str)
    all_completed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._checks_passed = True

    def run(self):
        import time

        self.check_started.emit("python")
        try:
            import sys
            time.sleep(0.1)
            version = f"Python {sys.version_info.major}.{sys.version_info.minor}"
            self.check_completed.emit("python", True, version)
        except Exception as e:
            self.check_completed.emit("python", False, str(e)[:15])
            self._checks_passed = False

        self.check_started.emit("pyqt")
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            time.sleep(0.1)
            self.check_completed.emit("pyqt", True, f"Qt {QT_VERSION_STR}")
        except Exception as e:
            self.check_completed.emit("pyqt", False, str(e)[:15])
            self._checks_passed = False

        self.check_started.emit("firebird")
        try:
            import firebirdsql
            time.sleep(0.1)
            self.check_completed.emit("firebird", True, "firebirdsql OK")
        except ImportError:
            self.check_completed.emit("firebird", False, "Não instalado")
        except Exception as e:
            self.check_completed.emit("firebird", False, str(e)[:15])

        self.check_started.emit("ncm_json")
        try:
            from refactored_sqltools.utils.ncm_manager import get_ncm_manager
            ncm_manager = get_ncm_manager()

            self.check_progress.emit("ncm_json", "Verificando...")
            d_success, d_msg = ncm_manager.download_json(
                lambda m: self.check_progress.emit("ncm_json", m[:12])
            )

            if d_success:
                self.check_progress.emit("ncm_json", "Carregando...")
                l_success, l_msg = ncm_manager.load_json()
                if not l_success:
                    self._checks_passed = False

                if "ja atualizado" in d_msg.lower():
                    status_msg = "Atualizado"
                else:
                    status_msg = "OK"
                self.check_completed.emit("ncm_json", l_success, status_msg)
            else:
                self.check_progress.emit("ncm_json", "Carregando (offline)...")
                l_success, _ = ncm_manager.load_json()
                if not l_success:
                    self._checks_passed = False
                self.check_completed.emit("ncm_json", l_success, "Offline")
        except Exception as e:
            self._checks_passed = False
            self.check_completed.emit("ncm_json", False, str(e)[:12])

        self.check_started.emit("dirs")
        try:
            time.sleep(0.1)

            required_modules = [
                'refactored_sqltools.core',
                'refactored_sqltools.ui',
                'refactored_sqltools.utils',
                'refactored_sqltools.config'
            ]

            missing = []
            for mod in required_modules:
                try:
                    __import__(mod)
                except ImportError:
                    missing.append(mod.split('.')[-1])

            if missing:
                self.check_completed.emit("dirs", False, f"Faltando: {len(missing)}")
            else:
                self.check_completed.emit("dirs", True, "OK")
        except Exception as e:
            self.check_completed.emit("dirs", False, str(e)[:12])

        self.check_started.emit("config")
        try:
            from refactored_sqltools.config import get_config_manager
            time.sleep(0.1)
            config = get_config_manager()
            conn = config.get_connection_config()
            db_type = conn.get('db_type', 'N/A')
            self.check_completed.emit("config", True, db_type)
        except Exception as e:
            self.check_completed.emit("config", False, str(e)[:12])

        self.all_completed.emit(self._checks_passed)


class SplashScreen(QWidget):
    """Tela de carregamento com Fluent Design - theme-aware."""

    loading_complete = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._check_items = {}
        self._setup_ui()

    def _setup_ui(self):
        dark = isDarkTheme()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 440)

        bg = "#1e1e2e" if dark else "#ffffff"
        border = "#2d2d3d" if dark else "#e0e0e0"
        self.setStyleSheet(f"""
            #SplashMain {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)
        self.setObjectName("SplashMain")

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 20)
        main_layout.setSpacing(10)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(90)
        self._load_logo()
        main_layout.addWidget(self.logo_label)

        title_label = TitleLabel("SQL SysHub")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.subtitle_label = CaptionLabel("Inicializando sistema...")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(f"color: {'#94a3b8' if dark else '#7f8c8d'};")
        main_layout.addWidget(self.subtitle_label)

        main_layout.addSpacing(5)

        container_bg = "#181825" if dark else "#f8f9fa"
        container_border = "#2d2d3d" if dark else "#e9ecef"
        checks_container = QFrame()
        checks_container.setStyleSheet(f"""
            QFrame {{
                background-color: {container_bg};
                border: 1px solid {container_border};
                border-radius: 6px;
            }}
        """)
        checks_layout = QVBoxLayout(checks_container)
        checks_layout.setContentsMargins(8, 8, 8, 8)
        checks_layout.setSpacing(1)

        checks = [
            ("python", "Ambiente Python"),
            ("pyqt", "Interface gráfica"),
            ("firebird", "Driver de banco de dados"),
            ("ncm_json", "Tabela NCM (Siscomex)"),
            ("dirs", "Estrutura do sistema"),
            ("config", "Configurações"),
        ]

        for check_id, check_text in checks:
            item = CheckItem(check_text)
            item.setStyleSheet("background: transparent;")
            self._check_items[check_id] = item
            checks_layout.addWidget(item)

        main_layout.addWidget(checks_container)

        main_layout.addSpacing(5)

        self.progress_bar = ProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        main_layout.addWidget(self.progress_bar)

        version_label = CaptionLabel("Versão 2.0.2")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(f"color: {'#64748b' if dark else '#adb5bd'};")
        main_layout.addWidget(version_label)

    def _load_logo(self):
        logo_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'imagens', 'cmLogo.png'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'imagens', 'cmLogo.png'),
            'imagens/cmLogo.png',
        ]

        for path in logo_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.logo_label.setPixmap(scaled)
                    return

        dark = isDarkTheme()
        self.logo_label.setText("SQL")
        self.logo_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {'#60a5fa' if dark else '#3498db'};")

    def _setup_worker(self):
        self.worker = LoadingWorker()
        self.worker.check_started.connect(self._on_check_started)
        self.worker.check_progress.connect(self._on_check_progress)
        self.worker.check_completed.connect(self._on_check_completed)
        self.worker.all_completed.connect(self._on_all_completed)

    def start_loading(self):
        self._setup_worker()
        self.worker.start()

    def _on_check_started(self, check_id: str):
        if check_id in self._check_items:
            self._check_items[check_id].set_running("Verificando...")

    def _on_check_progress(self, check_id: str, message: str):
        if check_id in self._check_items:
            self._check_items[check_id].set_running(message)

    def _on_check_completed(self, check_id: str, success: bool, message: str):
        if check_id in self._check_items:
            if success:
                self._check_items[check_id].set_success(message)
            elif check_id in ("ncm_json", "firebird"):
                self._check_items[check_id].set_warning(message)
            else:
                self._check_items[check_id].set_error(message)

    def _on_all_completed(self, success: bool):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)

        dark = isDarkTheme()
        if success:
            self.subtitle_label.setText("Sistema pronto!")
            self.subtitle_label.setStyleSheet(f"color: {'#4ade80' if dark else '#27ae60'}; font-weight: bold;")
        else:
            self.subtitle_label.setText("Iniciando com avisos...")
            self.subtitle_label.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'};")

        QTimer.singleShot(800, lambda: self.loading_complete.emit(success))
