# -*- coding: utf-8 -*-
"""
Main Window for SQL SysHub Application
Integrates all UI components into a cohesive Fluent Design interface.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QLabel, QMessageBox,
                            QScrollArea, QSizePolicy, QApplication, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from qfluentwidgets import (FluentWindow, FluentIcon, NavigationItemPosition,
                           PushButton, InfoBar, InfoBarPosition,
                           BodyLabel, TitleLabel, SimpleCardWidget,
                           HorizontalSeparator, isDarkTheme, qconfig)

from refactored_sqltools.ui.components.connection_panel import ConnectionPanel
from refactored_sqltools.ui.components.operation_selector import OperationSelector
from refactored_sqltools.ui.components.results_display import ResultsDisplay
from refactored_sqltools.ui.components.status_progress import StatusProgressWidget
from refactored_sqltools.ui.components.sql_editor import SQLEditorWidget
from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.workers.database_worker import DatabaseWorker, DatabaseWorkerFactory
from refactored_sqltools.config import get_config_manager
from refactored_sqltools.utils.paths import resolve_asset_path
from refactored_sqltools.ui.theme_manager import ThemeManager


class MainWindow(FluentWindow):
    """Main application window with Fluent Design."""

    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.setWindowTitle("SQL SysHub - Utilitarios de Banco de Dados")

        self.db_manager = DatabaseManager()
        self.worker = None
        self.config = get_config_manager()
        self.current_connection_params = None
        self._pending_connection_params = None
        self.state_tooltip = None

        ThemeManager.get_instance()

        # Create connection panel early (needed for signals)
        self.connection_panel = ConnectionPanel()

        self.setup_window()
        self.create_interfaces()
        self.connect_signals()

        self._try_auto_connect()

    def setup_window(self):
        screen = QApplication.primaryScreen().geometry()
        screen_w = screen.width()
        screen_h = screen.height()

        geometry = self.config.get_window_geometry()
        if geometry.get('maximized', False):
            w = min(max(900, int(screen_w * 0.8)), 1400)
            h = min(max(600, int(screen_h * 0.8)), 900)
            x = (screen_w - w) // 2
            y = (screen_h - h) // 2
        else:
            w = geometry.get('width', 1200)
            h = geometry.get('height', 800)
            x = geometry.get('x', (screen_w - w) // 2)
            y = geometry.get('y', (screen_h - h) // 2)

        self.setGeometry(x, y, w, h)
        self.setMinimumSize(800, 550)

        if geometry.get('maximized', False):
            self.showMaximized()

        self.titleBar.titleLabel.setText("SQL SysHub")

        qconfig.themeChanged.connect(self._on_theme_changed)

    def _set_conn_indicator(self, state: str):
        dark = isDarkTheme()
        if state == "connected":
            self.conn_indicator.setText("●")
            self.conn_indicator.setStyleSheet(f"color: {'#4ade80' if dark else '#27ae60'}; font-size: 14px;")
        elif state == "connecting":
            self.conn_indicator.setText("◌")
            self.conn_indicator.setStyleSheet(f"color: {'#fbbf24' if dark else '#f39c12'}; font-size: 14px;")
        else:
            self.conn_indicator.setText("○")
            self.conn_indicator.setStyleSheet(f"color: {'#64748b' if dark else '#bdc3c7'}; font-size: 14px;")

    def _on_theme_changed(self):
        self._update_status_style(self.status_label.text())

    def _update_status_style(self, text):
        dark = isDarkTheme()
        self.status_label.setStyleSheet(f"color: {'#94a3b8' if dark else '#666666'};")

    def create_interfaces(self):
        self.inicioInterface = QWidget()
        self.inicioInterface.setObjectName("inicioInterface")

        self.settingsInterface = QWidget()
        self.settingsInterface.setObjectName("settingsInterface")

        self.setup_inicio()
        self.setup_settings()

        self.addSubInterface(
            self.inicioInterface, FluentIcon.HOME, "Inicio"
        )
        self.addSubInterface(
            self.settingsInterface, FluentIcon.SETTING, "Configurações"
        )

        self.navigationInterface.addItem(
            routeKey="theme_toggle",
            icon=FluentIcon.PALETTE,
            text="Tema",
            onClick=lambda: ThemeManager.toggle_theme(),
            position=NavigationItemPosition.BOTTOM,
        )

    def setup_inicio(self):
        layout = QVBoxLayout(self.inicioInterface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)

        main_area = self.create_main_area()
        splitter.addWidget(main_area)

        sidebar.setMinimumWidth(300)
        sidebar.setMaximumWidth(360)
        main_area.setMinimumWidth(400)

        splitter.setSizes([320, 620])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        content_layout.addWidget(splitter)
        layout.addLayout(content_layout, 1)

        self.status_bar_widget = QWidget()
        self.status_bar_widget.setObjectName("statusBarWidget")
        self.status_bar_widget.setFixedHeight(28)
        sb_layout = QHBoxLayout(self.status_bar_widget)
        sb_layout.setContentsMargins(10, 1, 10, 1)
        sb_layout.setSpacing(4)

        self.conn_indicator = QLabel("○")
        self.conn_indicator.setFixedWidth(14)
        self.conn_indicator.setAlignment(Qt.AlignCenter)
        self._set_conn_indicator("disconnected")
        sb_layout.addWidget(self.conn_indicator)

        self.status_label = BodyLabel("Conecte-se ao banco para iniciar")
        self._update_status_style("Conecte-se ao banco para iniciar")
        sb_layout.addWidget(self.status_label, 1)

        self.status_progress = StatusProgressWidget()
        sb_layout.addWidget(self.status_progress)

        layout.addWidget(self.status_bar_widget)

    def create_sidebar(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("sidebarWidget")
        self.sidebar_widget.setStyleSheet("#sidebarWidget { background: transparent; }")
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        self.operation_selector = OperationSelector()
        sidebar_layout.addWidget(self.operation_selector)

        scroll.setWidget(self.sidebar_widget)
        return scroll

    def create_main_area(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        icon = QLabel()
        icon.setPixmap(FluentIcon.DEVELOPER_TOOLS.icon().pixmap(20, 20))
        title = TitleLabel("SQL SysHub")
        title_row.addWidget(icon)
        title_row.addWidget(title)
        title_row.addStretch()

        self.toggle_sql_btn = PushButton(FluentIcon.CODE, "")
        self.toggle_sql_btn.setToolTip("Mostrar/Ocultar SQL")
        self.toggle_sql_btn.clicked.connect(self.toggle_sql_display)
        title_row.addWidget(self.toggle_sql_btn)

        layout.addLayout(title_row)

        self.sql_group = QWidget()
        self.sql_group.setObjectName("sqlGroup")
        sql_layout = QVBoxLayout(self.sql_group)
        sql_layout.setContentsMargins(0, 0, 0, 0)
        self.sql_editor_widget = SQLEditorWidget()
        self.sql_editor_widget.setMinimumHeight(100)
        self.sql_editor_widget.setMaximumHeight(200)
        sql_layout.addWidget(self.sql_editor_widget)
        layout.addWidget(self.sql_group)
        self.sql_group.setVisible(False)

        self.results_display = ResultsDisplay()
        layout.addWidget(self.results_display, 1)

        return main_widget

    def setup_settings(self):
        layout = QVBoxLayout(self.settingsInterface)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = TitleLabel("Configurações")
        layout.addWidget(header)
        layout.addWidget(HorizontalSeparator())

        container = QWidget()
        container.setMaximumWidth(480)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.connection_panel)
        layout.addWidget(container)

        layout.addStretch()

    def connect_signals(self):
        self.connection_panel.connection_requested.connect(self.handle_connection_request)
        self.connection_panel.disconnection_requested.connect(self.handle_disconnection_request)
        self.connection_panel.connection_changed.connect(self.on_connection_changed)
        self.operation_selector.sql_updated.connect(self.update_sql_display)
        self.operation_selector.execute_requested.connect(self.execute_operation)
        self.results_display.cell_copied.connect(self.on_cell_copied)

    def _try_auto_connect(self):
        if not self.config.should_auto_connect():
            return
        if not self.config.should_remember_connection():
            return
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, self._do_auto_connect)

    def _do_auto_connect(self):
        try:
            params = self.connection_panel.get_connection_params()
            if not params.get('database'):
                return
            if not params.get('password'):
                self.config.set_auto_connect(False)
                return
            self.connection_panel.connection_requested.emit(
                params['db_type'], params['host'], params['port'],
                params['username'], params['password'], params['database']
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Auto-connect failed: {e}")

    def handle_connection_request(self, db_type, host, port, username, password, database):
        self._pending_connection_params = {
            'db_type': db_type, 'host': host, 'port': port,
            'username': username, 'password': password, 'database': database,
        }
        self.connection_panel.set_connecting_state()
        self.status_progress.set_connecting_state()
        self._set_conn_indicator("connecting")

        self.worker = DatabaseWorkerFactory.create_connection_worker(
            self.db_manager, db_type, host, port, username, password, database
        )
        self.worker.finished.connect(self.on_connection_finished)
        self.worker.progress.connect(self._update_progress)
        self.worker.start()

    def handle_disconnection_request(self):
        self.current_connection_params = None
        self._pending_connection_params = None
        self.connection_panel.update_status(False, "Desconectado")
        self.operation_selector.set_execute_enabled(False)
        self.results_display.clear()
        self._set_conn_indicator("disconnected")
        self._set_status("Desconectado do banco de dados")

    def on_connection_changed(self, connected):
        self.operation_selector.set_execute_enabled(connected)

    def on_connection_finished(self, success, message, result):
        self.connection_panel.reset_connection_state()
        if success:
            self.current_connection_params = self._pending_connection_params
            self._pending_connection_params = None
            self.connection_panel.update_status(True)
            self._set_conn_indicator("connected")
            self._set_status("Conectado com sucesso")
            self.status_progress.set_completed_state("Conectado")
        else:
            self.current_connection_params = None
            self._pending_connection_params = None
            self.connection_panel.update_status(False, "Erro na conexao")
            self._set_conn_indicator("disconnected")
            self._set_status("Falha na conexão")
            self.status_progress.set_error_state("Falha na conexão")
            InfoBar.error(
                title="Erro de Conexao",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def execute_operation(self):
        if not self.current_connection_params:
            InfoBar.warning(
                title="Aviso",
                content="Conecte-se ao banco de dados primeiro",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        if self.operation_selector.parameter_widgets:
            parameters = self.operation_selector.collect_parameters()
            if parameters is None:
                return
            self.operation_selector.current_parameters = parameters
            self.operation_selector.update_sql()

        operation = self.operation_selector.get_current_operation()
        if not operation:
            InfoBar.warning(
                title="Aviso",
                content="Selecione uma operacao",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        operation_name = operation['name']
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar Operacao")
        msg.setTextFormat(Qt.RichText)
        dark = isDarkTheme()
        warning_color = "#e74c3c" if not dark else "#f87171"
        msg.setText(f"<b> Deseja realmente executar a operação abaixo?</b><br>"
                    f"<span style='color: {warning_color};'>→ {operation_name}</span>")
        msg.setIcon(QMessageBox.Warning)
        sim_btn = msg.addButton("Sim", QMessageBox.YesRole)
        msg.addButton("Não", QMessageBox.NoRole)
        msg.exec_()
        if msg.clickedButton() != sim_btn:
            return

        self.operation_selector.set_execute_enabled(False)
        self.operation_selector.set_execute_text("EXECUTANDO...")
        self.results_display.clear()
        self.status_progress.set_executing_state(operation_name)

        operation_instance = operation.get('operation_instance')
        parameters = operation.get('parameters', {})

        self.worker = DatabaseWorkerFactory.create_custom_operation_worker(
            self.db_manager, operation_instance, operation_name,
            parameters, connection_config=self.current_connection_params,
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.progress.connect(self._update_progress)
        self.worker.start()

    def on_operation_finished(self, success, message, result):
        self.operation_selector.set_execute_enabled(True)
        self.operation_selector.set_execute_text("EXECUTAR OPERAÇÃO")
        self._hide_progress()

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

        self.results_display.display_operation_result(success, message, result_dict)

        if success:
            row_count = len(result.data) if result and result.data else 0
            fonte = f" | Fonte: {getattr(result, 'source', '')}" if result and getattr(result, 'source', None) else ""
            status_msg = f"Concluído - {row_count} registros{fonte}"
            self._set_status(status_msg)
            self.status_progress.set_completed_state(status_msg)
        else:
            self._set_status("Erro na operação")
            self.status_progress.set_error_state("Erro na operação")
            InfoBar.error(
                title="Erro na Operacao",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def _show_progress(self, message):
        self.status_label.setText(message)
        self.status_progress.show_progress(message)

    def _update_progress(self, value):
        self.status_progress.set_progress(value)

    def _hide_progress(self):
        self.status_progress.hide_progress()

    def _set_status(self, message):
        self.status_label.setText(message)
        self._update_status_style(message)

    def update_sql_display(self, sql):
        self.sql_editor_widget.set_sql_text(sql)

    def toggle_sql_display(self):
        is_visible = self.sql_group.isVisible()
        self.sql_group.setVisible(not is_visible)

    def on_cell_copied(self, text):
        display_text = text[:50] + "..." if len(text) > 50 else text
        self._set_status(f"Copiado: {display_text}")

    def cleanup(self):
        self.current_connection_params = None
        if self.db_manager.is_connected():
            self.db_manager.disconnect_all()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)

    def closeEvent(self, event):
        self._save_window_geometry()
        self.cleanup()
        event.accept()

    def _save_window_geometry(self):
        try:
            is_max = self.isMaximized()
            if is_max:
                g = self.normalGeometry()
                w, h, x, y = g.width(), g.height(), g.x(), g.y()
            else:
                w, h, x, y = self.width(), self.height(), self.x(), self.y()
            self.config.save_window_geometry(w, h, x, y, is_max)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to save window geometry: {e}")
