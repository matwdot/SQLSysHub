"""
Parameter Dialog with Fluent Design.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QFormLayout, QSpacerItem, QSizePolicy, QWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from qfluentwidgets import (PrimaryPushButton, PushButton, BodyLabel,
                           CaptionLabel, CardWidget, HorizontalSeparator)

from refactored_sqltools.ui.components.enhanced_parameters import (
    ParameterWidgetFactory, StyledDateEdit, EnhancedSpinBox,
    EnhancedLineEdit, EnhancedComboBox
)


class ParameterDialog(QDialog):
    """Dialog for collecting query parameters with Fluent Design."""

    parameters_confirmed = pyqtSignal(dict)

    def __init__(self, operation_name, parameters, parent=None):
        super().__init__(parent)
        self.operation_name = operation_name
        self.parameters = parameters
        self.parameter_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Parâmetros - {self.operation_name}")
        self.setModal(True)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = BodyLabel(f"Parâmetros: {self.operation_name}")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(HorizontalSeparator())

        card = CardWidget()
        params_layout = QFormLayout(card)
        params_layout.setSpacing(8)
        params_layout.setContentsMargins(12, 12, 12, 12)

        for param_name, param_config in self.parameters.items():
            param_type = param_config.get('type', 'text')
            param_label = param_config.get('label', param_name)

            label = CaptionLabel(f"{param_label}:")
            label.setToolTip(param_config.get('description', ''))

            widget = ParameterWidgetFactory.create_widget(param_config)

            self.parameter_widgets[param_name] = {
                'widget': widget,
                'type': param_type,
                'config': param_config
            }
            params_layout.addRow(label, widget)

        layout.addWidget(card)

        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        cancel_btn = PushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        ok_btn = PrimaryPushButton("Executar")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_parameters)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        if self.parameter_widgets:
            first_widget_info = list(self.parameter_widgets.values())[0]
            first_widget = first_widget_info['widget']
            if hasattr(first_widget, 'setFocus'):
                first_widget.setFocus()

    def accept_parameters(self):
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
                return

            if param_type in ('number', 'number_slider'):
                min_val = param_config.get('min')
                if min_val is not None and value < min_val:
                    from PyQt5.QtWidgets import QMessageBox
                    param_label = param_config.get('label', param_name)
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Erro de Validação")
                    msg.setText(f"O campo '{param_label}' deve ser maior ou igual a {min_val}.")
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
                    return

            if param_type in ('number', 'number_slider', 'decimal'):
                parameters[param_name] = str(value)
            elif param_type == 'date_range':
                parameters['data_inicio'] = value['start']
                parameters['data_fim'] = value['end']
            else:
                parameters[param_name] = value

        self.parameters_confirmed.emit(parameters)
        self.accept()

    def get_parameters(self):
        parameters = {}

        for param_name, widget_info in self.parameter_widgets.items():
            widget = widget_info['widget']
            param_type = widget_info['type']
            param_config = widget_info['config']

            value = ParameterWidgetFactory.get_value(widget, param_type)

            if param_type in ('number', 'number_slider'):
                min_val = param_config.get('min')
                if min_val is not None and value < min_val:
                    return None

            if param_type in ('number', 'number_slider', 'decimal'):
                parameters[param_name] = str(value)
            elif param_type == 'date_range':
                parameters['data_inicio'] = value['start']
                parameters['data_fim'] = value['end']
            else:
                parameters[param_name] = value

        return parameters


def show_parameter_dialog(operation_name, parameters, parent=None):
    """
    Convenience function to show parameter dialog and return parameters.
    """
    dialog = ParameterDialog(operation_name, parameters, parent)

    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_parameters()

    return None
