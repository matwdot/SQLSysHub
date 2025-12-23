# -*- coding: utf-8 -*-
"""
Main Window for SQL SysHub Application

Integrates all UI components into a cohesive interface.
Migrates window setup, styling, and layout from original SQL SysHub.py.
Connects component signals for inter-component communication.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QGroupBox, QPushButton,
                            QLabel, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
import qtawesome as qta

from refactored_sqltools.ui.components.connection_panel import ConnectionPanel
from refactored_sqltools.ui.components.operation_selector import OperationSelector
from refactored_sqltools.ui.components.results_display import ResultsDisplay
from refactored_sqltools.ui.components.progress_indicator import ProgressIndicator
from refactored_sqltools.ui.components.sql_editor import SQLEditorWidget
from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.workers.database_worker import DatabaseWorker, DatabaseWorkerFactory


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
        
        # Setup window
        self.setup_window()
        self.setup_ui()
        self.setup_styles()
        self.connect_signals()
    
    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("SQL SysHub - Utilitarios de Banco de Dados")
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon(r"C:\Dados\Projects\ncm-inexistente\imagens\cmLogo.png"))
        except:
            pass  # Icon file may not exist in all environments
        
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(900, 600)
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto", 0)  # Permanent message
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for sidebar and main area
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create sidebar and main area
        self.create_sidebar()
        self.create_main_area()
        
        # Add to splitter
        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(self.main_widget)
        splitter.setSizes([320, 680])
    
    def create_sidebar(self):
        """Create the sidebar with connection and operation controls"""
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        
        # Connection panel
        self.connection_panel = ConnectionPanel()
        sidebar_layout.addWidget(self.connection_panel)
        
        # Operation selector
        self.operation_selector = OperationSelector()
        sidebar_layout.addWidget(self.operation_selector)
        
        # Execute button
        self.execute_btn = QPushButton()
        play_icon = qta.icon('fa5s.play', color='white')
        self.execute_btn.setIcon(play_icon)
        self.execute_btn.setIconSize(QSize(16, 16))
        self.execute_btn.setText(" Executar")
        self.execute_btn.clicked.connect(self.execute_operation)
        self.execute_btn.setEnabled(False)
        self.execute_btn.setMinimumHeight(45)
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
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
        
        # Progress indicator
        self.progress_indicator = ProgressIndicator()
        sidebar_layout.addWidget(self.progress_indicator)
        
        sidebar_layout.addStretch()
    
    def create_main_area(self):
        """Create the main content area"""
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        
        # Title section with compact SQL toggle
        title_layout = QHBoxLayout()
        tools_icon = qta.icon('fa5s.tools', color='#2c3e50')
        icon_label = QLabel()
        icon_label.setPixmap(tools_icon.pixmap(32, 32))
        title_label = QLabel("SQL SysHub")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Compact SQL toggle button
        self.toggle_sql_btn = QPushButton()
        self.toggle_sql_btn.setObjectName("compactToggleButton")  # For specific styling
        eye_icon = qta.icon('fa5s.eye', color='#7f8c8d')
        self.toggle_sql_btn.setIcon(eye_icon)
        self.toggle_sql_btn.setToolTip("Mostrar SQL")
        self.toggle_sql_btn.clicked.connect(self.toggle_sql_display)
        title_layout.addWidget(self.toggle_sql_btn)
        
        main_layout.addLayout(title_layout)
        
        # SQL display group
        self.sql_group = QGroupBox("SQL a ser executado")
        sql_layout = QVBoxLayout(self.sql_group)
        
        # Use the new SQL editor widget
        self.sql_editor_widget = SQLEditorWidget()
        self.sql_editor_widget.setMinimumHeight(200)  # Increased minimum height
        self.sql_editor_widget.setMaximumHeight(400)  # Allow expansion up to 400px
        sql_layout.addWidget(self.sql_editor_widget)
        
        main_layout.addWidget(self.sql_group)
        self.sql_group.setVisible(False)  # Initially hidden
        
        # Results display
        self.results_display = ResultsDisplay()
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
    
    def handle_connection_request(self, db_type, host, port, username, password, database):
        """Handle connection request from connection panel"""
        # Update UI state
        self.connection_panel.set_connecting_state()
        self.progress_indicator.set_connecting_state()
        
        # Show connecting status
        self.show_info_status(f"Conectando ao banco {db_type}...", 0)  # Permanent until finished
        
        # Create and start worker
        self.worker = DatabaseWorkerFactory.create_connection_worker(
            self.db_manager, db_type, host, port, username, password, database
        )
        self.worker.finished.connect(self.on_connection_finished)
        self.worker.progress.connect(self.progress_indicator.set_progress)
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
        self.progress_indicator.hide_progress()
        self.connection_panel.reset_connection_state()
        
        if success:
            self.connection_panel.update_status(True)
            # Show success message in status bar instead of popup
            self.show_success_status(message, 8000)  # Show for 8 seconds
        else:
            self.connection_panel.update_status(False, "Erro na conexao")
            # Show error in status bar and popup for critical errors
            self.show_error_status(message, 10000)  # Show for 10 seconds
            
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
        msg_box.setText(f"Deseja realmente executar a operacao:")
        msg_box.setInformativeText(f"{operation_name}\n\n{operation['description']}")
        msg_box.setIcon(QMessageBox.Question)
        
        # Custom buttons in Portuguese
        sim_btn = msg_box.addButton("Sim", QMessageBox.YesRole)
        nao_btn = msg_box.addButton("Nao", QMessageBox.NoRole)
        
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
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
            QMessageBox QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        reply = msg_box.exec_()
        
        if msg_box.clickedButton() != sim_btn:
            return
        
        # Prepare UI
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("Executando...")
        self.progress_indicator.set_executing_state(operation_name)
        self.results_display.clear()
        
        # Show executing status
        self.show_info_status(f"Executando: {operation_name}...", 0)  # Permanent until finished
        
        # Get formatted SQL
        sql = self.operation_selector.get_formatted_sql()
        
        # Create and start worker
        self.worker = DatabaseWorkerFactory.create_query_worker(
            self.db_manager, sql, operation_name
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.progress.connect(self.progress_indicator.set_progress)
        self.worker.start()
    
    def on_operation_finished(self, success, message, result):
        """Handle operation completion"""
        self.progress_indicator.hide_progress()
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
        
        # Show message in status bar for success, popup only for errors
        if success:
            # Show success message in status bar
            self.show_success_status(message, 8000)  # Show for 8 seconds
        else:
            # Show error in status bar and popup for critical errors
            self.show_error_status(message, 10000)  # Show for 10 seconds
            
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
        self.cleanup()
        event.accept()
