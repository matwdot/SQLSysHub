"""
Operation Selector Component with Fluent Design.
Matches the reference design from insumos_ui/operação/.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QSizePolicy, QFrame, QFormLayout)
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QSize
from PyQt5.QtGui import QFont, QColor

from qfluentwidgets import (CardWidget, TreeWidget, TreeItemDelegate,
                           BodyLabel, CaptionLabel, ComboBox, LineEdit,
                           PrimaryPushButton, PushButton, CheckBox,
                           SwitchButton, HorizontalSeparator,
                           FluentIcon, IconWidget, isDarkTheme, qconfig)

from refactored_sqltools.core.operations.registry import operation_registry
from refactored_sqltools.ui.components.enhanced_parameters import (
    ParameterWidgetFactory, StyledDateEdit, EnhancedSpinBox,
    EnhancedLineEdit, EnhancedComboBox, NumberWithSlider
)
from refactored_sqltools.config import get_config_manager

from PyQt5.QtWidgets import QTreeWidgetItem


OPERATION_ICON_MAP = {
    "Cancelar Cupom": FluentIcon.CANCEL,
    "Apagar Certificado": FluentIcon.DELETE,
    "Corrigir Erro de Equipamento": FluentIcon.SYNC,
    "Limpar Tabelas do Fisco": FluentIcon.BROOM,
    "Consultar NCM Inexistente": FluentIcon.SEARCH,
    "Ver NCMs a Vencer": FluentIcon.DATE_TIME,
}

DEFAULT_ICON = FluentIcon.VIEW


class _SegmentedFilter(QWidget):
    """Segmented button group for filter selection (Ambos/PDV/Server)."""

    changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = {}
        self._active = None
        self._setup_ui()
        qconfig.themeChanged.connect(self._update_style)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._bg = QWidget()
        self._bg.setObjectName("segmentedBg")
        bg_layout = QHBoxLayout(self._bg)
        bg_layout.setContentsMargins(3, 3, 3, 3)
        bg_layout.setSpacing(6)

        for label, value in [("Ambos", "Ambos"), ("PDV", "PDV"), ("Server", "Server")]:
            btn = PushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setProperty("segment", True)
            btn.clicked.connect(lambda checked, v=value: self._on_click(v))
            self._buttons[value] = btn
            bg_layout.addWidget(btn)

        layout.addWidget(self._bg)

        self._update_style()
        self.setActive("Ambos")

    def _update_style(self):
        dark = isDarkTheme()
        bg = "#1e1e2e" if dark else "#eae7e7"
        border = "#2d2d3d" if dark else "#dcd9d9"
        self._bg.setStyleSheet(f"""
            #segmentedBg {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)

    def _on_click(self, value):
        self.setActive(value)

    def setActive(self, value):
        self._active = value
        for v, btn in self._buttons.items():
            checked = v == value
            btn.setChecked(checked)
        self.changed.emit(value)

    def active(self):
        return self._active


class _ParamField(QWidget):
    """A single parameter field with label above and input below."""

    def __init__(self, label_text, input_widget, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.label = CaptionLabel(label_text.upper())
        self.label.setStyleSheet("font-weight: 700; letter-spacing: 0.5px;")
        layout.addWidget(self.label)

        self.input = input_widget
        layout.addWidget(self.input)


class OperationSelector(QWidget):
    """Operation selector panel matching the Fluent SQL Core design."""

    operation_changed = pyqtSignal(str)
    sql_updated = pyqtSignal(str)
    parameters_requested = pyqtSignal(str, dict)
    execute_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_operation_name = None
        self.current_parameters = {}
        self.parameter_widgets = {}
        self.parameters_config = {}
        self.config = get_config_manager()
        self.setup_ui()
        self.load_operations()
        qconfig.themeChanged.connect(self._apply_theme)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = CardWidget()
        card.setObjectName("OperationSelector")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── CONTEXTO DA OPERAÇÃO ──
        card_layout.addWidget(self._section_label("CONTEXTO DA OPERAÇÃO"))

        filter_container = QWidget()
        filter_container.setObjectName("filterContainer")
        filter_container.setContentsMargins(16, 4, 16, 8)
        fc_layout = QVBoxLayout(filter_container)
        fc_layout.setContentsMargins(0, 0, 0, 0)
        self.filter = _SegmentedFilter()
        self.filter.changed.connect(self._on_filter_changed)
        fc_layout.addWidget(self.filter)
        card_layout.addWidget(filter_container)

        sep = HorizontalSeparator()
        sep.setFixedHeight(1)
        card_layout.addWidget(sep)

        # ── AÇÕES DISPONÍVEIS ──
        card_layout.addWidget(self._section_label("AÇÕES DISPONÍVEIS"))

        tree_container = QWidget()
        tree_container.setObjectName("treeContainer")
        tree_container.setContentsMargins(8, 2, 8, 4)
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self.operation_tree = TreeWidget()
        self.operation_tree.setHeaderHidden(True)
        self.operation_tree.setIndentation(8)
        self.operation_tree.setIconSize(QSize(18, 18))
        self.operation_tree.itemClicked.connect(self.on_operation_changed)
        tree_layout.addWidget(self.operation_tree)
        card_layout.addWidget(tree_container)

        self.operation_description = CaptionLabel()
        self.operation_description.setWordWrap(True)
        self.operation_description.setContentsMargins(16, 0, 16, 4)
        self.operation_description.setMaximumHeight(32)
        self.operation_description.setOpenExternalLinks(True)
        card_layout.addWidget(self.operation_description)

        # ── PARÂMETROS (after operations, shown only when needed) ──
        sep2 = HorizontalSeparator()
        sep2.setFixedHeight(1)
        sep2.setVisible(False)
        self._params_sep = sep2
        card_layout.addWidget(sep2)

        self.params_header = self._section_label("PARÂMETROS")
        self.params_header.setVisible(False)
        card_layout.addWidget(self.params_header)

        self.parameters_frame = QFrame()
        self.parameters_frame.setObjectName("parametersFrame")
        self.parameters_frame.setVisible(False)
        params_inner = QVBoxLayout(self.parameters_frame)
        params_inner.setContentsMargins(16, 4, 16, 8)
        params_inner.setSpacing(6)

        self.parameters_form = QFormLayout()
        self.parameters_form.setSpacing(6)
        self.parameters_form.setContentsMargins(0, 0, 0, 0)
        params_inner.addLayout(self.parameters_form)
        card_layout.addWidget(self.parameters_frame)

        # ── EXECUTAR ──
        exec_container = QWidget()
        exec_container.setObjectName("execContainer")
        exec_container.setContentsMargins(16, 4, 16, 16)
        ec_layout = QVBoxLayout(exec_container)
        ec_layout.setContentsMargins(0, 0, 0, 0)

        self.execute_btn = PrimaryPushButton("EXECUTAR OPERAÇÃO")
        self.execute_btn.setIcon(FluentIcon.PLAY)
        self.execute_btn.clicked.connect(self._on_execute)
        self.execute_btn.setEnabled(False)
        self.execute_btn.setMinimumHeight(36)
        ec_layout.addWidget(self.execute_btn)

        card_layout.addWidget(exec_container)

        layout.addWidget(card)
        
        self._apply_container_transparency()

    def _section_label(self, text):
        lbl = CaptionLabel(text.upper())
        lbl.setContentsMargins(16, 12, 16, 6)
        dark = isDarkTheme()
        label_color = "#e2e8f0" if dark else "#2c3e50"
        lbl.setStyleSheet(f"font-weight: 700; letter-spacing: 1.2px; color: {label_color};")
        return lbl

    def _apply_theme(self):
        """Update all theme-dependent visuals when theme changes"""
        dark = isDarkTheme()
        label_color = "#e2e8f0" if dark else "#2c3e50"

        self._apply_container_transparency()

        # Update section labels
        for lbl_text in ["CONTEXTO DA OPERAÇÃO", "AÇÕES DISPONÍVEIS", "PARÂMETROS"]:
            for child in self.findChildren(CaptionLabel):
                if child.text() == lbl_text:
                    child.setStyleSheet(f"font-weight: 700; letter-spacing: 1.2px; color: {label_color};")

        # Update parameter labels currently visible in the form
        for i in range(self.parameters_form.count()):
            item = self.parameters_form.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), CaptionLabel):
                item.widget().setStyleSheet(f"font-weight: 700; letter-spacing: 0.5px; color: {label_color};")

    def _apply_container_transparency(self):
        """Ensure container widgets are transparent to show CardWidget background"""
        transparent = "background: transparent; border: none;"
        for container in self.findChildren(QWidget):
            name = container.objectName()
            if name in ("filterContainer", "treeContainer", "execContainer"):
                container.setStyleSheet(f"#{name} {{ {transparent} }}")
        self.parameters_frame.setStyleSheet("QFrame#parametersFrame { background: transparent; border: none; }")

    def _on_filter_changed(self, value):
        self.load_operations()

    def get_selected_types(self):
        active = self.filter.active()
        if active == "Ambos":
            return ["PDV", "Server", "Ambos"]
        return [active]

    def load_operations(self):
        selected_types = self.get_selected_types()
        operations_by_session = operation_registry.get_operations_by_type(selected_types)

        current_selection = None
        current_item = self.operation_tree.currentItem()
        if current_item:
            current_selection = current_item.data(0, Qt.UserRole)

        self.operation_tree.clear()

        all_operations = []
        for session_name, operations in operations_by_session.items():
            for operation_name in operations.keys():
                all_operations.append(operation_name)

        all_operations.sort()

        for operation_name in all_operations:
            item = QTreeWidgetItem(self.operation_tree)
            item.setText(0, operation_name)
            item.setData(0, Qt.UserRole, operation_name)

            icon = OPERATION_ICON_MAP.get(operation_name, DEFAULT_ICON)
            item.setIcon(0, icon.icon())

        if current_selection and current_selection in all_operations:
            self.set_operation(current_selection)
        else:
            last_operation = self.config.get_last_operation()
            if last_operation and last_operation in all_operations:
                self.set_operation(last_operation)
            elif all_operations:
                first_item = self.operation_tree.topLevelItem(0)
                if first_item:
                    self.operation_tree.setCurrentItem(first_item)
                    self.on_operation_changed(first_item, 0)

    def on_operation_changed(self, item=None, column=None):
        if item is None:
            item = self.operation_tree.currentItem()
        if not item:
            return

        operation_name = item.data(0, Qt.UserRole)
        if not operation_name:
            return

        try:
            operation = operation_registry.get_operation(operation_name)
            self.current_operation_name = operation_name
            self.config.set_last_operation(operation_name)

            self.operation_description.setText(operation.description)

            if operation_registry.has_parameters(operation_name):
                self.parameters_config = operation_registry.get_operation_parameters(operation_name)
                self.show_inline_parameters(operation_name, self.parameters_config)
            else:
                self.current_parameters = {}
                self.parameters_config = {}
                self.hide_inline_parameters()
                self.update_sql()

            self.operation_changed.emit(operation_name)

        except KeyError:
            self.operation_description.setText("Operação não encontrada no registry")
            self.hide_inline_parameters()

    def show_inline_parameters(self, operation_name, parameters_config):
        self.clear_parameter_widgets()
        self.params_header.setVisible(True)
        self._params_sep.setVisible(True)

        dark = isDarkTheme()
        label_color = "#e2e8f0" if dark else "#2c3e50"

        for param_name, param_config in parameters_config.items():
            param_type = param_config.get('type', 'text')
            param_label = param_config.get('label', param_name)

            # Create label as CaptionLabel (bold, uppercase style)
            label = CaptionLabel(param_label.upper())
            label.setStyleSheet(f"font-weight: 700; letter-spacing: 0.5px; color: {label_color};")

            widget = ParameterWidgetFactory.create_widget(param_config)

            self.parameter_widgets[param_name] = {
                'widget': widget,
                'type': param_type,
                'config': param_config
            }

            self.parameters_form.addRow(label, widget)

        self.parameters_frame.setVisible(True)

        if self.parameter_widgets:
            first_widget_info = list(self.parameter_widgets.values())[0]
            first_widget = first_widget_info['widget']
            if hasattr(first_widget, 'setFocus'):
                first_widget.setFocus()

    def hide_inline_parameters(self):
        self.clear_parameter_widgets()
        self.parameters_frame.setVisible(False)
        self.params_header.setVisible(False)
        self._params_sep.setVisible(False)

    def clear_parameter_widgets(self):
        while self.parameters_form.count():
            item = self.parameters_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.parameter_widgets = {}

    def collect_parameters(self):
        parameters = {}

        for param_name, widget_info in self.parameter_widgets.items():
            widget = widget_info['widget']
            param_type = widget_info['type']
            param_config = widget_info['config']

            value = ParameterWidgetFactory.get_value(widget, param_type)

            if param_config.get('required') and not value:
                from PyQt5.QtWidgets import QMessageBox
                param_label = param_config.get('label', param_name)
                msg = QMessageBox(self)
                msg.setWindowTitle("Campo Obrigatório")
                msg.setText(f"O campo '{param_label}' é obrigatório.")
                msg.setIcon(QMessageBox.Warning)
                
                # Style the message box with theme awareness
                dark = isDarkTheme()
                bg_color = "#2d2d3d" if dark else "white"
                text_color = "#e2e8f0" if dark else "#2c3e50"
                button_bg = "#e74c3c" if not dark else "#c0392b"
                button_hover = "#c0392b" if not dark else "#e74c3c"
                button_pressed = "#a93226" if not dark else "#923121"
                
                msg.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {bg_color};
                        color: {text_color};
                        font-size: 12px;
                    }}
                    QMessageBox QLabel {{
                        color: {text_color};
                        padding: 10px;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {button_bg};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background-color: {button_hover};
                    }}
                    QMessageBox QPushButton:pressed {{
                        background-color: {button_pressed};
                    }}
                """)
                
                msg.exec_()
                if hasattr(widget, 'setFocus'):
                    widget.setFocus()
                return None

            if param_type in ('number', 'number_slider'):
                if param_config.get('min') is not None and value < param_config['min']:
                    from PyQt5.QtWidgets import QMessageBox
                    param_label = param_config.get('label', param_name)
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Erro de Validação")
                    msg.setText(f"O campo '{param_label}' deve ser maior ou igual a {param_config['min']}.")
                    msg.setIcon(QMessageBox.Warning)
                    
                    # Style the message box with theme awareness
                    dark = isDarkTheme()
                    bg_color = "#2d2d3d" if dark else "white"
                    text_color = "#e2e8f0" if dark else "#2c3e50"
                    button_bg = "#e74c3c" if not dark else "#c0392b"
                    button_hover = "#c0392b" if not dark else "#e74c3c"
                    button_pressed = "#a93226" if not dark else "#923121"
                    
                    msg.setStyleSheet(f"""
                        QMessageBox {{
                            background-color: {bg_color};
                            color: {text_color};
                            font-size: 12px;
                        }}
                        QMessageBox QLabel {{
                            color: {text_color};
                            padding: 10px;
                        }}
                        QMessageBox QPushButton {{
                            background-color: {button_bg};
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px 20px;
                            font-weight: bold;
                            min-width: 80px;
                        }}
                        QMessageBox QPushButton:hover {{
                            background-color: {button_hover};
                        }}
                        QMessageBox QPushButton:pressed {{
                            background-color: {button_pressed};
                        }}
                    """)
                    
                    msg.exec_()
                    if hasattr(widget, 'setFocus'):
                        widget.setFocus()
                    return None

            if param_type in ('number', 'number_slider', 'decimal'):
                parameters[param_name] = str(value)
            elif param_type == 'date_range':
                parameters['data_inicio'] = value['start']
                parameters['data_fim'] = value['end']
            else:
                parameters[param_name] = value

        return parameters

    def update_sql(self):
        if not self.current_operation_name:
            return

        try:
            operation = operation_registry.get_operation(self.current_operation_name)

            if self.current_parameters:
                sql = operation.get_sql(**self.current_parameters)
            else:
                sql = operation.get_sql()

            check_sql = operation.get_check_sql()
            if check_sql:
                sql = f"-- Verificação:\n{check_sql}\n\n-- Execução:\n{sql}"

            self.sql_updated.emit(sql)

        except Exception as e:
            self.sql_updated.emit(f"-- Erro ao gerar SQL: {str(e)}")

    def set_parameters(self, parameters):
        self.current_parameters = parameters
        self.update_sql()

    def get_current_operation(self):
        if not self.current_operation_name:
            return None

        try:
            operation = operation_registry.get_operation(self.current_operation_name)

            return {
                'name': self.current_operation_name,
                'description': operation.description,
                'operation_instance': operation,
                'parameters': self.current_parameters.copy()
            }
        except KeyError:
            return None

    def get_formatted_sql(self):
        if not self.current_operation_name:
            return ""

        try:
            operation = operation_registry.get_operation(self.current_operation_name)
            if self.current_parameters:
                sql = operation.get_sql(**self.current_parameters)
            else:
                sql = operation.get_sql()
            return sql
        except Exception as e:
            return f"-- Erro ao gerar SQL: {str(e)}"

    def set_operation(self, operation_name):
        try:
            operation_registry.get_operation(operation_name)

            for i in range(self.operation_tree.topLevelItemCount()):
                operation_item = self.operation_tree.topLevelItem(i)
                if operation_item.data(0, Qt.UserRole) == operation_name:
                    self.operation_tree.setCurrentItem(operation_item)
                    self.on_operation_changed(operation_item, 0)
                    return
        except KeyError:
            pass

    def set_execute_enabled(self, enabled):
        self.execute_btn.setEnabled(enabled)

    def set_execute_text(self, text):
        self.execute_btn.setText(text)

    def _on_execute(self):
        self.execute_requested.emit()
