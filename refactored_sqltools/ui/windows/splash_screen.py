"""
Splash Screen - Tela de Carregamento

Exibe uma tela de carregamento elegante com verificações do sistema.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap


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
        
        # Ícone de status
        self.icon_label = QLabel("○")
        self.icon_label.setFixedWidth(18)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("color: #bdc3c7; font-size: 11px;")
        
        # Texto da verificação
        self.text_label = QLabel(self.text)
        self.text_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        
        # Mensagem de status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setMinimumWidth(100)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.status_label)
        
    def set_running(self, message: str = ""):
        self.icon_label.setText("●")
        self.icon_label.setStyleSheet("color: #3498db; font-size: 11px;")
        self.text_label.setStyleSheet("color: #3498db; font-size: 11px; font-weight: bold;")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #3498db; font-size: 10px;")
        QApplication.processEvents()
        
    def set_success(self, message: str = ""):
        self.icon_label.setText("✓")
        self.icon_label.setStyleSheet("color: #27ae60; font-size: 11px; font-weight: bold;")
        self.text_label.setStyleSheet("color: #2c3e50; font-size: 11px;")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        QApplication.processEvents()
        
    def set_error(self, message: str = ""):
        self.icon_label.setText("✗")
        self.icon_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: bold;")
        self.text_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 10px;")
        QApplication.processEvents()
        
    def set_warning(self, message: str = ""):
        self.icon_label.setText("!")
        self.icon_label.setStyleSheet("color: #f39c12; font-size: 11px; font-weight: bold;")
        self.text_label.setStyleSheet("color: #f39c12; font-size: 11px;")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #f39c12; font-size: 10px;")
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
        """Executa todas as verificações."""
        import time
        
        # 1. Verificar ambiente Python
        self.check_started.emit("python")
        try:
            import sys
            time.sleep(0.1)
            version = f"Python {sys.version_info.major}.{sys.version_info.minor}"
            self.check_completed.emit("python", True, version)
        except Exception as e:
            self.check_completed.emit("python", False, str(e)[:15])
            self._checks_passed = False
        
        # 2. Verificar PyQt5
        self.check_started.emit("pyqt")
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            time.sleep(0.1)
            self.check_completed.emit("pyqt", True, f"Qt {QT_VERSION_STR}")
        except Exception as e:
            self.check_completed.emit("pyqt", False, str(e)[:15])
            self._checks_passed = False
        
        # 3. Verificar driver Firebird
        self.check_started.emit("firebird")
        try:
            import fdb
            time.sleep(0.1)
            self.check_completed.emit("firebird", True, "FDB OK")
        except ImportError:
            self.check_completed.emit("firebird", False, "Não instalado")
        except Exception as e:
            self.check_completed.emit("firebird", False, str(e)[:15])

        # 4. Verificar arquivo JSON de NCM
        self.check_started.emit("ncm_json")
        try:
            from refactored_sqltools.utils.ncm_manager import get_ncm_manager
            ncm_manager = get_ncm_manager()
            
            available, _ = ncm_manager.is_json_available()
            
            if available:
                self.check_progress.emit("ncm_json", "Carregando...")
                success, load_msg = ncm_manager.load_json()
                if success:
                    self.check_completed.emit("ncm_json", True, "Carregado")
                else:
                    self.check_completed.emit("ncm_json", False, "Erro")
            else:
                self.check_progress.emit("ncm_json", "Baixando...")
                success, _ = ncm_manager.download_json(lambda m: self.check_progress.emit("ncm_json", m[:12]))
                
                if success:
                    self.check_progress.emit("ncm_json", "Carregando...")
                    load_success, _ = ncm_manager.load_json()
                    self.check_completed.emit("ncm_json", load_success, "OK" if load_success else "Erro")
                else:
                    self.check_completed.emit("ncm_json", False, "Sem conexão")
        except Exception as e:
            self.check_completed.emit("ncm_json", False, str(e)[:12])
        
        # 5. Verificar estrutura do sistema (módulos carregados)
        self.check_started.emit("dirs")
        try:
            time.sleep(0.1)
            
            # Verificar se os módulos principais estão disponíveis
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
        
        # 6. Verificar configurações
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
    """Tela de carregamento com verificações do sistema."""
    
    loading_complete = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self._check_items = {}
        self._setup_ui()
        self._setup_worker()
        
    def _setup_ui(self):
        # Janela sem bordas, fundo branco sólido
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 420)
        
        # Fundo branco com borda cinza sutil
        self.setStyleSheet("""
            QWidget#SplashMain {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
            }
        """)
        self.setObjectName("SplashMain")
        
        # Centralizar na tela
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(10)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(90)
        self._load_logo()
        main_layout.addWidget(self.logo_label)
        
        # Título
        title_label = QLabel("SQL SysHub")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; background: transparent;")
        main_layout.addWidget(title_label)
        
        # Subtítulo
        self.subtitle_label = QLabel("Inicializando sistema...")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 11px; color: #7f8c8d; background: transparent;")
        main_layout.addWidget(self.subtitle_label)
        
        # Espaçador
        main_layout.addSpacing(5)
        
        # Container de verificações
        checks_container = QFrame()
        checks_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }
        """)
        checks_layout = QVBoxLayout(checks_container)
        checks_layout.setContentsMargins(5, 8, 5, 8)
        checks_layout.setSpacing(1)
        
        # Itens de verificação
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
        
        # Espaçador
        main_layout.addSpacing(5)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #e9ecef;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setRange(0, 0)
        main_layout.addWidget(self.progress_bar)
        
        # Versão
        version_label = QLabel("Versão 2.0.1")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 9px; color: #adb5bd; background: transparent;")
        main_layout.addWidget(version_label)
        
    def _load_logo(self):
        """Carrega a logo do sistema."""
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
        
        # Fallback
        self.logo_label.setText("SQL")
        self.logo_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db; background: transparent;")
        
    def _setup_worker(self):
        self.worker = LoadingWorker()
        self.worker.check_started.connect(self._on_check_started)
        self.worker.check_progress.connect(self._on_check_progress)
        self.worker.check_completed.connect(self._on_check_completed)
        self.worker.all_completed.connect(self._on_all_completed)
        
    def start_loading(self):
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
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if success:
            self.subtitle_label.setText("Sistema pronto!")
            self.subtitle_label.setStyleSheet("font-size: 11px; color: #27ae60; font-weight: bold; background: transparent;")
        else:
            self.subtitle_label.setText("Iniciando com avisos...")
            self.subtitle_label.setStyleSheet("font-size: 11px; color: #f39c12; background: transparent;")
        
        QTimer.singleShot(800, lambda: self.loading_complete.emit(success))
