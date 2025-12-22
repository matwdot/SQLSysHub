"""
Connection Panel Component

Extracts connection UI logic from original SysPDVUtilsGUI.
Implements PyQt5 signals for connection state changes.
Provides database type selection and parameter input.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QGroupBox)
from PyQt5.QtCore import pyqtSignal
import qtawesome as qta


class ConnectionPanel(QWidget):
    """Reusable connection panel component"""
    
    # Signals
    connection_requested = pyqtSignal(str, str, str, str, str, str)  # db_type, host, port, username, password, database
    disconnection_requested = pyqtSignal()
    connection_changed = pyqtSignal(bool)  # True if connected, False if disconnected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.setup_ui()
        self.setup_styles()
        
        # Initialize default values
        self.on_db_type_change()
    
    def setup_ui(self):
        """Setup the connection panel UI"""
        layout = QVBoxLayout(self)
        
        # Connection group
        connection_group = QGroupBox("Conexão ao Banco")
        connection_group.setStyleSheet("QGroupBox::title { padding-left: 20px; }")
        connection_layout = QGridLayout(connection_group)
        
        # Database type
        connection_layout.addWidget(QLabel("Tipo:"), 0, 0)
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["Firebird", "SQL Server"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_change)
        connection_layout.addWidget(self.db_type_combo, 0, 1)
        
        # Host
        connection_layout.addWidget(QLabel("Host:"), 1, 0)
        self.host_entry = QLineEdit("localhost")
        connection_layout.addWidget(self.host_entry, 1, 1)
        
        # Port
        connection_layout.addWidget(QLabel("Porta:"), 2, 0)
        self.port_entry = QLineEdit("3050")
        connection_layout.addWidget(self.port_entry, 2, 1)
        
        # Username
        connection_layout.addWidget(QLabel("Usuário:"), 3, 0)
        self.username_entry = QLineEdit("SYSDBA")
        connection_layout.addWidget(self.username_entry, 3, 1)
        
        # Password
        connection_layout.addWidget(QLabel("Senha:"), 4, 0)
        self.password_entry = QLineEdit("masterkey")
        self.password_entry.setEchoMode(QLineEdit.Password)
        connection_layout.addWidget(self.password_entry, 4, 1)
        
        # Database
        connection_layout.addWidget(QLabel("Database:"), 5, 0)
        self.database_combo = QComboBox()
        self.database_combo.currentTextChanged.connect(self.on_database_option_changed)
        connection_layout.addWidget(self.database_combo, 5, 1)
        
        # Custom database field
        self.custom_db_entry = QLineEdit()
        self.custom_db_entry.setVisible(False)
        connection_layout.addWidget(self.custom_db_entry, 6, 0, 1, 2)
        
        # Connect button
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.clicked.connect(self.handle_connection)
        connection_layout.addWidget(self.connect_btn, 7, 0, 1, 2)
        
        # Status label
        self.status_label = QLabel()
        self.update_status(False, "Desconectado")
        connection_layout.addWidget(self.status_label, 8, 0, 1, 2)
        
        layout.addWidget(connection_group)
    
    def setup_styles(self):
        """Setup component styles"""
        self.setStyleSheet("""
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
                font-size: 12px;
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
            QLineEdit, QComboBox {
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
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Arquivo de banco de dados não encontrado:\n\n{database}\n\nVerifique o caminho e tente novamente."
                )
                return
            
            self.connection_requested.emit(db_type, host, port, username, password, database)
    
    def update_status(self, connected, message=""):
        """Update connection status display"""
        self.is_connected = connected
        
        if connected:
            connected_icon = qta.icon('fa5s.circle', color='#27ae60')
            self.status_label.setPixmap(connected_icon.pixmap(20, 20))
            self.status_label.setText(" Conectado")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 13px;")
            self.connect_btn.setText("Desconectar")
        else:
            disconnected_icon = qta.icon('fa5s.circle', color='#e74c3c')
            self.status_label.setPixmap(disconnected_icon.pixmap(20, 20))
            self.status_label.setText(f" {message}" if message else " Desconectado")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 13px;")
            self.connect_btn.setText("Conectar")
        
        self.connection_changed.emit(connected)
    
    def set_connecting_state(self):
        """Set UI to connecting state"""
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Conectando...")
        connecting_icon = qta.icon('fa5s.circle', color='#f39c12')
        self.status_label.setPixmap(connecting_icon.pixmap(20, 20))
        self.status_label.setText(" Conectando...")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 13px;")
    
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