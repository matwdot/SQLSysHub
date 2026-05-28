"""
Database connection panel with Fluent Design widgets.
"""

import os

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                            QMessageBox, QSizePolicy, QSpacerItem)

from qfluentwidgets import (CardWidget, ComboBox, LineEdit, PushButton,
                           PrimaryPushButton, BodyLabel, CaptionLabel,
                           HorizontalSeparator)

from refactored_sqltools.config import get_config_manager
from refactored_sqltools.utils.credential_store import (
    load_password, make_credential_key, save_password,
)


class ConnectionPanel(QWidget):
    """Reusable database connection panel with Fluent Design."""

    connection_requested = pyqtSignal(str, str, str, str, str, str)
    disconnection_requested = pyqtSignal()
    connection_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.config = get_config_manager()
        self.setup_ui()
        self._load_saved_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        card_layout.addWidget(self._section_header("Conexão ao Banco"))
        card_layout.addWidget(HorizontalSeparator())

        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(16, 12, 16, 12)
        form_layout.setSpacing(8)

        self._add_field(form_layout, "Tipo:", self._make_db_combo())
        self._add_field(form_layout, "Host:", self._make_host_entry())
        self._add_field(form_layout, "Porta:", self._make_port_entry())
        self._add_field(form_layout, "Usuário:", self._make_username_entry())
        self._add_field(form_layout, "Senha:", self._make_password_entry())
        self._add_field(form_layout, "Database:", self._make_database_combo())

        self.custom_db_entry = LineEdit()
        self.custom_db_entry.setVisible(False)
        self.custom_db_entry.setPlaceholderText("Caminho do banco...")
        form_layout.addWidget(self.custom_db_entry)

        card_layout.addWidget(form)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(16, 0, 16, 12)
        btn_row.setSpacing(8)

        self.connect_btn = PrimaryPushButton("Conectar")
        self.connect_btn.clicked.connect(self.handle_connection)
        self.connect_btn.setMinimumHeight(32)
        btn_row.addWidget(self.connect_btn)

        self.status_label = CaptionLabel("Desconectado")
        self.status_label.setAlignment(Qt.AlignCenter)
        btn_row.addWidget(self.status_label)

        card_layout.addLayout(btn_row)

        layout.addWidget(card)

    def _section_header(self, text):
        lbl = BodyLabel(text)
        lbl.setContentsMargins(16, 12, 16, 8)
        return lbl

    def _add_field(self, parent_layout, label_text, field_widget):
        row = QHBoxLayout()
        row.setSpacing(8)
        label = CaptionLabel(label_text)
        label.setFixedWidth(64)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(label)
        row.addWidget(field_widget, 1)
        parent_layout.addLayout(row)

    def _make_db_combo(self):
        self.db_type_combo = ComboBox()
        self.db_type_combo.addItems(["Firebird", "SQL Server"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_change)
        return self.db_type_combo

    def _make_host_entry(self):
        self.host_entry = LineEdit()
        self.host_entry.setText("localhost")
        return self.host_entry

    def _make_port_entry(self):
        self.port_entry = LineEdit()
        self.port_entry.setText("3050")
        return self.port_entry

    def _make_username_entry(self):
        self.username_entry = LineEdit()
        self.username_entry.setText("SYSDBA")
        return self.username_entry

    def _make_password_entry(self):
        self.password_entry = LineEdit()
        self.password_entry.setEchoMode(LineEdit.EchoMode.Password)
        return self.password_entry

    def _make_database_combo(self):
        self.database_combo = ComboBox()
        self.database_combo.currentTextChanged.connect(self.on_database_option_changed)
        return self.database_combo

    def on_db_type_change(self):
        db_type = self.db_type_combo.currentText()

        if db_type == "Firebird":
            self.host_entry.setText("localhost")
            self.port_entry.setText("3050")
            self.username_entry.setText("SYSDBA")
            self.password_entry.setText("")
            self.database_combo.clear()
            self.database_combo.addItems(["SRV", "CAD", "MOV", "Custom"])
            self.database_combo.setCurrentIndex(0)
        elif db_type == "SQL Server":
            self.host_entry.setText("localhost")
            self.port_entry.setText("1433")
            self.username_entry.setText("sa")
            self.password_entry.setText("")
            self.database_combo.clear()
            self.database_combo.addItems(["syspdv", "master", "Custom"])
            self.database_combo.setCurrentIndex(0)

        self.on_database_option_changed()

    def on_database_option_changed(self):
        self.custom_db_entry.setVisible(self.database_combo.currentText() == "Custom")

    def handle_connection(self):
        if self.is_connected:
            self.disconnection_requested.emit()
            return

        params = self.get_connection_params()
        database = params["database"]

        if params["db_type"] == "Firebird" and database and not os.path.exists(database):
            QMessageBox.critical(
                self,
                "Erro",
                f"Arquivo de banco de dados nao encontrado:\n{database}",
            )
            return

        self.connection_requested.emit(
            params["db_type"], params["host"], params["port"],
            params["username"], params["password"], params["database"],
        )

    def _reset_button_style(self):
        self.connect_btn.setStyleSheet("")
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)

    def update_status(self, connected, message=""):
        from qfluentwidgets import isDarkTheme
        self.is_connected = connected
        dark = isDarkTheme()
        if connected:
            self.status_label.setText("Conectado")
            self.status_label.setStyleSheet(f"color: {'#4ade80' if dark else '#27ae60'}; font-weight: bold;")
            self.connect_btn.setText("Desconectar")
            self.connect_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#dc2626' if dark else '#e74c3c'};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {'#b91c1c' if dark else '#c0392b'};
                }}
                QPushButton:pressed {{
                    background-color: {'#991b1b' if dark else '#a93226'};
                }}
            """)
            self.save_connection_config()
        else:
            self.status_label.setText(message or "Desconectado")
            self.status_label.setStyleSheet(f"color: {'#f87171' if dark else '#e74c3c'};")
            self.connect_btn.setText("Conectar")
            self._reset_button_style()
        self.connection_changed.emit(connected)

    def set_connecting_state(self):
        from qfluentwidgets import isDarkTheme
        dark = isDarkTheme()
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Conectando...")
        self.status_label.setText("Conectando...")
        self.status_label.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'};")

    def reset_connection_state(self):
        self.connect_btn.setEnabled(True)

    def get_connection_params(self):
        db_type = self.db_type_combo.currentText()
        host = self.host_entry.text() or "localhost"
        port = self.port_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        database = self._resolve_database_value(db_type)

        return {
            "db_type": db_type, "host": host, "port": port,
            "username": username, "password": password, "database": database,
        }

    def _load_saved_config(self):
        if not self.config.should_remember_connection():
            self.on_db_type_change()
            return

        try:
            conn_config = self.config.get_connection_config()
            db_type = conn_config.get("db_type", "Firebird")
            index = self.db_type_combo.findText(db_type)
            if index >= 0:
                self.db_type_combo.blockSignals(True)
                self.db_type_combo.setCurrentIndex(index)
                self.db_type_combo.blockSignals(False)

            self._setup_database_options(db_type)
            self.host_entry.setText(conn_config.get("host", "localhost"))
            self.port_entry.setText(conn_config.get("port", "3050"))
            self.username_entry.setText(conn_config.get("username", "SYSDBA"))
            self.password_entry.setText("")

            db_option = conn_config.get("database_option", "SRV")
            index = self.database_combo.findText(db_option)
            if index >= 0:
                self.database_combo.setCurrentIndex(index)

            custom_db = conn_config.get("custom_database", "")
            if custom_db:
                self.custom_db_entry.setText(custom_db)

            self.on_database_option_changed()
            self._load_saved_password()
        except Exception:
            self.on_db_type_change()

    def _setup_database_options(self, db_type: str):
        self.database_combo.clear()
        if db_type == "Firebird":
            self.database_combo.addItems(["SRV", "CAD", "MOV", "Custom"])
        else:
            self.database_combo.addItems(["syspdv", "master", "Custom"])

    def save_connection_config(self):
        if not self.config.should_remember_connection():
            return

        db_type = self.db_type_combo.currentText()
        host = self.host_entry.text()
        port = self.port_entry.text()
        username = self.username_entry.text()
        database_option = self.database_combo.currentText()
        custom_database = self.custom_db_entry.text() if database_option == "Custom" else ""

        self.config.save_connection_config(
            db_type=db_type, host=host, port=port, username=username,
            database_option=database_option, custom_database=custom_database,
        )

        key = self._credential_key()
        save_password(key, self.password_entry.text())

    def _load_saved_password(self):
        password = load_password(self._credential_key())
        if password:
            self.password_entry.setText(password)

    def _credential_key(self) -> str:
        db_type = self.db_type_combo.currentText()
        return make_credential_key(
            db_type, self.host_entry.text() or "localhost",
            self.port_entry.text(), self.username_entry.text(),
            self._resolve_database_value(db_type),
        )

    def _resolve_database_value(self, db_type: str) -> str:
        if self.database_combo.currentText() == "Custom":
            return self.custom_db_entry.text()

        if db_type == "Firebird":
            paths = {
                "SRV": r"C:\Syspdv\syspdv_srv.fdb",
                "CAD": r"C:\Syspdv\syspdv_cad.fdb",
                "MOV": r"C:\Syspdv\syspdv_mov.fdb",
            }
            return paths.get(self.database_combo.currentText(), "")

        return self.database_combo.currentText()
