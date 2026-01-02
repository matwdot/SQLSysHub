"""
Connection Panel Component

Extracts connection UI logic from original SysPDVUtilsGUI.
Implements PyQt5 signals for connection state changes.
Provides database type selection and parameter input.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QGroupBox,
                            QSizePolicy)
from PyQt5.QtCore import pyqtSignal
import qtawesome as qta

from refactored_sqltools.config import get_config_manager


class ConnectionPanel(QWidget):
    """Reusable connection panel component"""
    
    # Signals
    connection_requested = pyqtSignal(str, str, str, str, str, str)  # db_type, host, port, username, password, database
    disconnection_requested = pyqtSignal()
    connection_changed = pyqtSignal(bool)  # True if connected, False if disconnected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.config = get_config_manager()
        self.setup_ui()
        self.setup_styles()
        
        # Load saved configuration
        self._load_saved_config()
    
    def setup_ui(self):
        """Setup the connection panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Connection group
        connection_group = QGroupBox("Conexão ao Banco")
        connection_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        connection_layout = QGridLayout(connection_group)
        connection_layout.setContentsMargins(8, 12, 8, 8)
        connection_layout.setSpacing(4)
        connection_layout.setVerticalSpacing(3)
        
        # Set column stretch
        connection_layout.setColumnStretch(0, 0)
        connection_layout.setColumnStretch(1, 1)
        
        row = 0
        
        # Database type
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_tipo, row, 0)
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["Firebird", "SQL Server"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_change)
        connection_layout.addWidget(self.db_type_combo, row, 1)
        row += 1
        
        # Host
        lbl_host = QLabel("Host:")
        lbl_host.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_host, row, 0)
        self.host_entry = QLineEdit("localhost")
        connection_layout.addWidget(self.host_entry, row, 1)
        row += 1
        
        # Port
        lbl_porta = QLabel("Porta:")
        lbl_porta.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_porta, row, 0)
        self.port_entry = QLineEdit("3050")
        connection_layout.addWidget(self.port_entry, row, 1)
        row += 1
        
        # Username
        lbl_usuario = QLabel("Usuário:")
        lbl_usuario.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_usuario, row, 0)
        self.username_entry = QLineEdit("SYSDBA")
        connection_layout.addWidget(self.username_entry, row, 1)
        row += 1
        
        # Password
        lbl_senha = QLabel("Senha:")
        lbl_senha.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_senha, row, 0)
        self.password_entry = QLineEdit("masterkey")
        self.password_entry.setEchoMode(QLineEdit.Password)
        connection_layout.addWidget(self.password_entry, row, 1)
        row += 1
        
        # Database
        lbl_db = QLabel("Database:")
        lbl_db.setStyleSheet("font-size: 11px;")
        connection_layout.addWidget(lbl_db, row, 0)
        self.database_combo = QComboBox()
        self.database_combo.currentTextChanged.connect(self.on_database_option_changed)
        connection_layout.addWidget(self.database_combo, row, 1)
        row += 1
        
        # Custom database field
        self.custom_db_entry = QLineEdit()
        self.custom_db_entry.setVisible(False)
        self.custom_db_entry.setPlaceholderText("Caminho do banco...")
        connection_layout.addWidget(self.custom_db_entry, row, 0, 1, 2)
        row += 1
        
        # Connect button
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.clicked.connect(self.handle_connection)
        self.connect_btn.setMinimumHeight(28)
        self.connect_btn.setMaximumHeight(34)
        connection_layout.addWidget(self.connect_btn, row, 0, 1, 2)
        row += 1
        
        # Status label
        self.status_label = QLabel()
        self.update_status(False, "Desconectado")
        self.status_label.setMinimumHeight(18)
        self.status_label.setWordWrap(True)
        connection_layout.addWidget(self.status_label, row, 0, 1, 2)
        
        layout.addWidget(connection_group)
    
    def setup_styles(self):
        """Setup component styles"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-height: 22px;
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
            QLineEdit, QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 4px 6px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
                min-height: 18px;
                max-height: 24px;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 11px;
            }
            QComboBox:hover, QLineEdit:hover {
                border: 1px solid #3498db;
            }
            QLabel {
                font-size: 11px;
                color: #2c3e50;
            }
        """)
    
    def on_db_type_change(self):
        """Handle database type change"""
        db_type = self.db_type_combo.currentText()
        
        if db_type == "Firebird":
            self.host_entry.setText("localhost")
            self.port_entry.setText("3050")
            self.username_entry.setText("SYSDBA")
            self.password_entry.setText("masterkey")
            self.database_combo.clear()
            self.database_combo.addItems(["SRV", "CAD", "MOV", "Custom"])
            self.database_combo.setCurrentIndex(0)
            self.custom_db_entry.setVisible(False)
        elif db_type == "SQL Server":
            self.host_entry.setText("localhost")
            self.port_entry.setText("1433")
            self.username_entry.setText("sa")
            self.password_entry.setText("")
            self.database_combo.clear()
            self.database_combo.addItems(["syspdv", "master", "Custom"])
            self.database_combo.setCurrentIndex(0)
            self.custom_db_entry.setVisible(False)
    
    def on_database_option_changed(self):
        """Show or hide custom database field"""
        if self.database_combo.currentText() == "Custom":
            self.custom_db_entry.setVisible(True)
        else:
            self.custom_db_entry.setVisible(False)
    
    def handle_connection(self):
        """Handle connect/disconnect button click"""
        if self.is_connected:
            self.disconnection_requested.emit()
        else:
            # Validate and emit connection request
            db_type = self.db_type_combo.currentText()
            host = self.host_entry.text() or "localhost"
            port = self.port_entry.text()
            username = self.username_entry.text()
            password = self.password_entry.text()
            
            # Determine database
            if self.database_combo.currentText() == "Custom":
                database = self.custom_db_entry.text()
            else:
                if db_type == "Firebird":
                    paths = {
                        "SRV": r"C:\Syspdv\syspdv_srv.fdb",
                        "CAD": r"C:\Syspdv\syspdv_cad.fdb",
                        "MOV": r"C:\Syspdv\syspdv_mov.fdb"
                    }
                    database = paths.get(self.database_combo.currentText(), "")
                else:
                    database = self.database_combo.currentText()
            
            # Validate Firebird file existence
            if db_type == "Firebird" and database and not os.path.exists(database):
                from PyQt5.QtWidgets import QMessageBox
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Erro")
                msg_box.setText("Arquivo de banco de dados não encontrado")
                msg_box.setInformativeText(f"Caminho: {database}\n\nVerifique o caminho e tente novamente.")
                msg_box.setIcon(QMessageBox.Critical)
                
                # Custom OK button in Portuguese
                ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
                
                # Style the message box
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                        color: #2c3e50;
                        font-size: 12px;
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
                return
            
            self.connection_requested.emit(db_type, host, port, username, password, database)
    
    def update_status(self, connected, message=""):
        """Update connection status display"""
        self.is_connected = connected
        
        if connected:
            self.status_label.setText("● Conectado")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            self.connect_btn.setText("Desconectar")
            # Salvar configurações após conexão bem-sucedida
            self.save_connection_config()
        else:
            self.status_label.setText(f"● {message}" if message else "● Desconectado")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 11px;")
            self.connect_btn.setText("Conectar")
        
        self.connection_changed.emit(connected)
    
    def set_connecting_state(self):
        """Set UI to connecting state"""
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Conectando...")
        self.status_label.setText("● Conectando...")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 11px;")
    
    def reset_connection_state(self):
        """Reset connection button state"""
        self.connect_btn.setEnabled(True)
    
    def get_connection_params(self):
        """Get current connection parameters"""
        db_type = self.db_type_combo.currentText()
        host = self.host_entry.text() or "localhost"
        port = self.port_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        
        # Determine database
        if self.database_combo.currentText() == "Custom":
            database = self.custom_db_entry.text()
        else:
            if db_type == "Firebird":
                paths = {
                    "SRV": r"C:\Syspdv\syspdv_srv.fdb",
                    "CAD": r"C:\Syspdv\syspdv_cad.fdb",
                    "MOV": r"C:\Syspdv\syspdv_mov.fdb"
                }
                database = paths.get(self.database_combo.currentText(), "")
            else:
                database = self.database_combo.currentText()
        
        return {
            'db_type': db_type,
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database
        }
    
    def _load_saved_config(self):
        """Carrega as configurações salvas do arquivo INI."""
        if not self.config.should_remember_connection():
            self.on_db_type_change()
            return
            
        try:
            conn_config = self.config.get_connection_config()
            
            # Definir tipo de banco (isso dispara on_db_type_change)
            db_type = conn_config.get('db_type', 'Firebird')
            index = self.db_type_combo.findText(db_type)
            if index >= 0:
                # Bloquear sinal temporariamente para evitar reset
                self.db_type_combo.blockSignals(True)
                self.db_type_combo.setCurrentIndex(index)
                self.db_type_combo.blockSignals(False)
            
            # Configurar opções do combo de database baseado no tipo
            self._setup_database_options(db_type)
            
            # Carregar valores salvos
            self.host_entry.setText(conn_config.get('host', 'localhost'))
            self.port_entry.setText(conn_config.get('port', '3050'))
            self.username_entry.setText(conn_config.get('username', 'SYSDBA'))
            self.password_entry.setText(conn_config.get('password', 'masterkey'))
            
            # Definir opção de database
            db_option = conn_config.get('database_option', 'SRV')
            index = self.database_combo.findText(db_option)
            if index >= 0:
                self.database_combo.setCurrentIndex(index)
            
            # Definir caminho customizado
            custom_db = conn_config.get('custom_database', '')
            if custom_db:
                self.custom_db_entry.setText(custom_db)
            
            # Mostrar/ocultar campo customizado
            self.on_database_option_changed()
            
        except Exception as e:
            # Em caso de erro, usar valores padrão
            self.on_db_type_change()
    
    def _setup_database_options(self, db_type: str):
        """Configura as opções do combo de database."""
        self.database_combo.clear()
        if db_type == "Firebird":
            self.database_combo.addItems(["SRV", "CAD", "MOV", "Custom"])
        else:
            self.database_combo.addItems(["syspdv", "master", "Custom"])
    
    def save_connection_config(self):
        """Salva as configurações de conexão atuais."""
        if not self.config.should_remember_connection():
            return
            
        db_type = self.db_type_combo.currentText()
        host = self.host_entry.text()
        port = self.port_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        database_option = self.database_combo.currentText()
        custom_database = self.custom_db_entry.text() if database_option == "Custom" else ""
        
        self.config.save_connection_config(
            db_type=db_type,
            host=host,
            port=port,
            username=username,
            password=password,
            database_option=database_option,
            custom_database=custom_database
        )