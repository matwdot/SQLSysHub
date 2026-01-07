# -*- coding: utf-8 -*-
"""
Main Window for SQL SysHub Application

Integrates all UI components into a cohesive interface.
Migrates window setup, styling, and layout from original SQL SysHub.py.
Connects component signals for inter-component communication.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QGroupBox, QPushButton,
                            QLabel, QMessageBox, QStatusBar, QScrollArea,
                            QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
import qtawesome as qta

from refactored_sqltools.ui.components.connection_panel import ConnectionPanel
from refactored_sqltools.ui.components.operation_selector import OperationSelector
from refactored_sqltools.ui.components.results_display import ResultsDisplay
from refactored_sqltools.ui.components.status_progress import StatusProgressWidget
from refactored_sqltools.ui.components.sql_editor import SQLEditorWidget
from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.workers.database_worker import DatabaseWorker, DatabaseWorkerFactory
from refactored_sqltools.config import get_config_manager


class MainWindow(QMainWindow):
    """
    Main application window that integrates all UI components.
    
    This class brings together the connection panel, operation selector,
    results display, and progress indicator into a cohesive interface,
    managing their interactions and database operations.
    """
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.db_manager = DatabaseManager()
        self.worker = None
        self.config = get_config_manager()
        
        # Setup window
        self.setup_window()
        self.setup_ui()
        self.setup_styles()
        self.connect_signals()
        
        # Auto-connect if enabled
        self._try_auto_connect()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("SQL SysHub - Utilitarios de Banco de Dados")
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon(r"C:\Dados\Projects\ncm-inexistente\imagens\cmLogo.png"))
        except:
            pass  # Icon file may not exist in all environments
        
        # Get screen size for responsive sizing
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Load window geometry from config
        geometry = self.config.get_window_geometry()
        
        # Use saved geometry or calculate defaults
        if geometry.get('maximized', False):
            window_width = min(max(900, int(screen_width * 0.8)), 1400)
            window_height = min(max(600, int(screen_height * 0.8)), 900)
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        else:
            window_width = geometry.get('width', 1200)
            window_height = geometry.get('height', 800)
            x = geometry.get('x', (screen_width - window_width) // 2)
            y = geometry.get('y', (screen_height - window_height) // 2)
            
            # Ensure window is within screen bounds
            if x < 0 or x + window_width > screen_width:
                x = (screen_width - window_width) // 2
            if y < 0 or y + window_height > screen_height:
                y = (screen_height - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
        
        # Maximize if saved as maximized
        if geometry.get('maximized', False):
            self.showMaximized()
        
        # Set minimum size to prevent layout breaking
        self.setMinimumSize(800, 550)
        
        # Setup status bar with progress widget
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress widget to status bar (initially hidden)
        self.status_progress = StatusProgressWidget()
        self.status_progress.setVisible(False)
        self.status_bar.addWidget(self.status_progress, 1)
        
        # Show default message
        self.status_bar.showMessage("Pronto")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create splitter for sidebar and main area
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Create sidebar with scroll area
        self.create_sidebar()
        self.create_main_area()
        
        # Add to splitter
        self.splitter.addWidget(self.sidebar_scroll)
        self.splitter.addWidget(self.main_widget)
        
        # Set minimum sizes
        self.sidebar_scroll.setMinimumWidth(260)
        self.sidebar_scroll.setMaximumWidth(400)
        self.main_widget.setMinimumWidth(350)
        
        # Set initial sizes with proper proportions
        self.splitter.setSizes([280, 520])
        
        # Set stretch factors (sidebar less stretchable than main area)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
    
    def create_sidebar(self):
        """Create the sidebar with connection and operation controls"""
        # Create scroll area for sidebar
        self.sidebar_scroll = QScrollArea()
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sidebar_scroll.setFrameShape(QScrollArea.NoFrame)
        self.sidebar_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
        """)
        
        # Sidebar content widget
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(2, 2, 2, 2)
        sidebar_layout.setSpacing(3)
        
        # Connection panel
        self.connection_panel = ConnectionPanel()
        self.connection_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sidebar_layout.addWidget(self.connection_panel)
        
        # Operation selector
        self.operation_selector = OperationSelector()
        self.operation_selector.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sidebar_layout.addWidget(self.operation_selector)
        
        # Execute button
        self.execute_btn = QPushButton()
        play_icon = qta.icon('fa5s.play', color='white')
        self.execute_btn.setIcon(play_icon)
        self.execute_btn.setIconSize(QSize(12, 12))
        self.execute_btn.setText(" Executar")
        self.execute_btn.clicked.connect(self.execute_operation)
        self.execute_btn.setEnabled(False)
        self.execute_btn.setMinimumHeight(22)
        self.execute_btn.setMaximumHeight(26)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
                min-height: 18px;
                max-height: 22px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        sidebar_layout.addWidget(self.execute_btn)
        
        # Add stretch to push everything to the top
        sidebar_layout.addStretch()
        
        # Set sidebar widget to scroll area
        self.sidebar_scroll.setWidget(self.sidebar_widget)
    
    def create_main_area(self):
        """Create the main content area"""
        self.main_widget = QWidget()
        self.main_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Title section with compact SQL toggle
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
        tools_icon = qta.icon('fa5s.tools', color='#2c3e50')
        icon_label = QLabel()
        icon_label.setPixmap(tools_icon.pixmap(24, 24))
        title_label = QLabel("SQL SysHub")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 6px;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Compact SQL toggle button
        self.toggle_sql_btn = QPushButton()
        self.toggle_sql_btn.setObjectName("compactToggleButton")
        eye_icon = qta.icon('fa5s.eye', color='#7f8c8d')
        self.toggle_sql_btn.setIcon(eye_icon)
        self.toggle_sql_btn.setToolTip("Mostrar SQL")
        self.toggle_sql_btn.clicked.connect(self.toggle_sql_display)
        title_layout.addWidget(self.toggle_sql_btn)
        
        main_layout.addLayout(title_layout)
        
        # SQL display group
        self.sql_group = QGroupBox("SQL a ser executado")
        sql_layout = QVBoxLayout(self.sql_group)
        sql_layout.setContentsMargins(6, 6, 6, 6)
        
        # Use the new SQL editor widget
        self.sql_editor_widget = SQLEditorWidget()
        self.sql_editor_widget.setMinimumHeight(120)
        self.sql_editor_widget.setMaximumHeight(250)
        sql_layout.addWidget(self.sql_editor_widget)
        
        main_layout.addWidget(self.sql_group)
        self.sql_group.setVisible(False)  # Initially hidden
        
        # Results display
        self.results_display = ResultsDisplay()
        self.results_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.results_display)
    
    def setup_styles(self):
        """Setup application-wide styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QPushButton#compactToggleButton {
                background-color: transparent;
                color: #7f8c8d;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 4px;
                font-size: 10px;
                min-width: 20px;
                min-height: 20px;
                max-width: 24px;
                max-height: 24px;
            }
            QPushButton#compactToggleButton:hover {
                background-color: #ecf0f1;
                color: #34495e;
                border-color: #95a5a6;
            }
            QPushButton#compactToggleButton:pressed {
                background-color: #d5dbdb;
                color: #2c3e50;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #2c3e50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #41aaf0;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #bdc3c7;
                color: #2c3e50;
                font-size: 13px;
                padding: 6px 12px;
                min-height: 20px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
    
    def connect_signals(self):
        """Connect signals between components"""
        # Connection panel signals
        self.connection_panel.connection_requested.connect(self.handle_connection_request)
        self.connection_panel.disconnection_requested.connect(self.handle_disconnection_request)
        self.connection_panel.connection_changed.connect(self.on_connection_changed)
        
        # Operation selector signals
        self.operation_selector.sql_updated.connect(self.update_sql_display)
        
        # Results display signals
        self.results_display.cell_copied.connect(self.on_cell_copied)
    
    def _try_auto_connect(self):
        """Tenta conectar automaticamente se a opção estiver habilitada."""
        if not self.config.should_auto_connect():
            return
        
        if not self.config.should_remember_connection():
            return
        
        # Usar QTimer para executar após a janela ser exibida
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, self._do_auto_connect)
    
    def _do_auto_connect(self):
        """Executa a conexão automática."""
        try:
            # Obter parâmetros de conexão do painel (já carregados do config)
            params = self.connection_panel.get_connection_params()
            
            if not params.get('database'):
                return
            
            # Emitir sinal de conexão
            self.connection_panel.connection_requested.emit(
                params['db_type'],
                params['host'],
                params['port'],
                params['username'],
                params['password'],
                params['database']
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Auto-connect failed: {e}")
    
    def handle_connection_request(self, db_type, host, port, username, password, database):
        """Handle connection request from connection panel"""
        # Update UI state
        self.connection_panel.set_connecting_state()
        self.status_progress.set_connecting_state()
        
        # Create and start worker
        self.worker = DatabaseWorkerFactory.create_connection_worker(
            self.db_manager, db_type, host, port, username, password, database
        )
        self.worker.finished.connect(self.on_connection_finished)
        self.worker.progress.connect(self.status_progress.set_progress)
        self.worker.start()
    
    def handle_disconnection_request(self):
        """Handle disconnection request from connection panel"""
        self.db_manager.disconnect()
        self.connection_panel.update_status(False, "Desconectado")
        self.execute_btn.setEnabled(False)
        self.results_display.clear()
        
        # Show disconnection status
        self.show_info_status("Desconectado do banco de dados", 3000)
    
    def on_connection_changed(self, connected):
        """Handle connection state change"""
        self.execute_btn.setEnabled(connected)
    
    def on_connection_finished(self, success, message, result):
        """Handle connection operation completion"""
        self.connection_panel.reset_connection_state()
        
        if success:
            self.connection_panel.update_status(True)
            self.status_progress.set_completed_state("Conectado com sucesso")
        else:
            self.connection_panel.update_status(False, "Erro na conexao")
            self.status_progress.set_error_state("Falha na conexão")
            
            # Custom error dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro de Conexao")
            msg_box.setText("Falha ao conectar com o banco de dados")
            msg_box.setInformativeText(message)
            msg_box.setIcon(QMessageBox.Critical)
            
            # Custom OK button
            ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
            
            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2c3e50;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    padding: 10px;
                }
                QMessageBox QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c0392b;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            
            msg_box.exec_()
    
    def execute_operation(self):
        """Execute the selected database operation"""
        if not self.db_manager.is_connected():
            # Custom warning dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Aviso")
            msg_box.setText("Conecte-se ao banco de dados primeiro")
            msg_box.setInformativeText("E necessario estabelecer uma conexao antes de executar operacoes.")
            msg_box.setIcon(QMessageBox.Warning)
            
            # Custom OK button
            ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
            
            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2c3e50;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    padding: 10px;
                }
                QMessageBox QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #e67e22;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #d35400;
                }
            """)
            
            msg_box.exec_()
            return
        
        # Collect parameters from inline widgets if operation has parameters
        if self.operation_selector.parameter_widgets:
            parameters = self.operation_selector.collect_parameters()
            if parameters is None:
                # Validation failed
                return
            self.operation_selector.current_parameters = parameters
            self.operation_selector.update_sql()
        
        # Get current operation
        operation = self.operation_selector.get_current_operation()
        if not operation:
            # Custom warning dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Aviso")
            msg_box.setText("Selecione uma operacao")
            msg_box.setInformativeText("Escolha uma operacao da lista antes de executar.")
            msg_box.setIcon(QMessageBox.Warning)
            
            # Custom OK button
            ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
            
            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2c3e50;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    padding: 10px;
                }
                QMessageBox QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #e67e22;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #d35400;
                }
            """)
            
            msg_box.exec_()
            return
        
        operation_name = operation['name']
        
        # Confirm operation
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar Operacao")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(f"""<b> Deseja realmente executar a operação abaixo?</b><br>
<span style='color: #c0392b;'>→ {operation_name}</span>""")
        msg_box.setIcon(QMessageBox.Warning)
        
        # Custom buttons in Portuguese
        sim_btn = msg_box.addButton("Sim", QMessageBox.YesRole)
        nao_btn = msg_box.addButton("Não", QMessageBox.NoRole)
        
        # Estilo base para ambos os botões
        button_style = """
            QPushButton {
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
        """
        
        sim_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        nao_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #c0392b;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Style the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                padding: 10px;
            }
        """)
        
        reply = msg_box.exec_()
        
        if msg_box.clickedButton() != sim_btn:
            return
        
        # Prepare UI
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executando...")
        self.status_progress.set_executing_state(operation_name)
        self.results_display.clear()
        
        # Check if operation has custom execute method
        operation_instance = operation.get('operation_instance')
        parameters = operation.get('parameters', {})
        
        # Lista de operações que usam execute customizado
        custom_execute_operations = ['Ver NCMs a Vencer']
        
        if operation_name in custom_execute_operations and operation_instance:
            # Usar worker para operação customizada (execução assíncrona)
            self.worker = DatabaseWorkerFactory.create_custom_operation_worker(
                self.db_manager, operation_instance, operation_name, parameters
            )
            self.worker.finished.connect(self.on_operation_finished)
            self.worker.progress.connect(self.status_progress.set_progress)
            self.worker.start()
            return
        
        # Fallback: usar SQL direto (comportamento padrão)
        sql = self.operation_selector.get_formatted_sql()
        
        # Create and start worker
        self.worker = DatabaseWorkerFactory.create_query_worker(
            self.db_manager, sql, operation_name
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.progress.connect(self.status_progress.set_progress)
        self.worker.start()
    
    def on_operation_finished(self, success, message, result):
        """Handle operation completion"""
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText(" Executar")
        
        # Convert QueryResult to dict format for results display
        result_dict = None
        if result:
            result_dict = {
                'success': result.success,
                'message': result.message
            }
            if result.columns:
                result_dict['columns'] = result.columns
                result_dict['data'] = result.data
            if result.rows_affected is not None:
                result_dict['rows_affected'] = result.rows_affected
        
        # Display results
        self.results_display.display_operation_result(success, message, result_dict)
        
        # Update status progress
        if success:
            row_count = len(result.data) if result and result.data else 0
            self.status_progress.set_completed_state(f"Concluído - {row_count} registros")
        else:
            self.status_progress.set_error_state("Erro na operação")
            
            # Custom error dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro na Operacao")
            msg_box.setText("Falha ao executar a operacao")
            msg_box.setInformativeText(message)
            msg_box.setIcon(QMessageBox.Critical)
            
            # Custom OK button
            ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
            
            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2c3e50;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    padding: 10px;
                }
                QMessageBox QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c0392b;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            
            msg_box.exec_()
    
    def update_sql_display(self, sql):
        """Update the SQL display with new SQL text"""
        self.sql_editor_widget.set_sql_text(sql)
    
    def toggle_sql_display(self):
        """Toggle SQL display visibility"""
        is_visible = self.sql_group.isVisible()
        self.sql_group.setVisible(not is_visible)
        
        if not is_visible:
            eye_slash_icon = qta.icon('fa5s.eye-slash', color='#7f8c8d')
            self.toggle_sql_btn.setIcon(eye_slash_icon)
            self.toggle_sql_btn.setToolTip("Ocultar SQL")
        else:
            eye_icon = qta.icon('fa5s.eye', color='#7f8c8d')
            self.toggle_sql_btn.setIcon(eye_icon)
            self.toggle_sql_btn.setToolTip("Mostrar SQL")
    
    def show_status_message(self, message, timeout=5000):
        """Show a temporary message in the status bar"""
        self.status_bar.showMessage(message, timeout)
    
    def show_permanent_status(self, message):
        """Show a permanent message in the status bar"""
        self.status_bar.showMessage(message, 0)
    
    def show_success_status(self, message, timeout=5000):
        """Show a success message in the status bar"""
        self.status_bar.showMessage(f"Sucesso: {message}", timeout)
    
    def show_error_status(self, message, timeout=8000):
        """Show an error message in the status bar"""
        self.status_bar.showMessage(f"Erro: {message}", timeout)
    
    def show_info_status(self, message, timeout=3000):
        """Show an info message in the status bar"""
        self.status_bar.showMessage(f"Info: {message}", timeout)
    
    def on_cell_copied(self, text):
        """Handle cell content copied to clipboard"""
        # Truncate text if too long for status bar
        display_text = text[:50] + "..." if len(text) > 50 else text
        self.show_success_status(f"Copiado: {display_text}", 3000)
    
    def cleanup(self):
        """Clean up application resources"""
        # Clean up database connections
        if self.db_manager.is_connected():
            self.db_manager.disconnect_all()
        
        # Stop any running workers
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)  # Wait up to 1 second
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry before closing
        self._save_window_geometry()
        self.cleanup()
        event.accept()
    
    def _save_window_geometry(self):
        """Save current window geometry to config"""
        try:
            is_maximized = self.isMaximized()
            if is_maximized:
                # When maximized, save the normal geometry
                geometry = self.normalGeometry()
                width = geometry.width()
                height = geometry.height()
                x = geometry.x()
                y = geometry.y()
            else:
                width = self.width()
                height = self.height()
                x = self.x()
                y = self.y()
            
            self.config.save_window_geometry(width, height, x, y, is_maximized)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to save window geometry: {e}")
