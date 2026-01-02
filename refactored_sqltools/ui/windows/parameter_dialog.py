"""
Parameter Dialog

Dialog window for collecting query parameters from user.
Opens as a separate window when queries have variables.
Uses enhanced parameter widgets for better UX.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QDateEdit, QLineEdit, QFormLayout,
                            QGroupBox, QSpacerItem, QSizePolicy, QWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from refactored_sqltools.ui.components.enhanced_parameters import (
    ParameterWidgetFactory, StyledDateEdit, EnhancedSpinBox, 
    EnhancedLineEdit, EnhancedComboBox
)


class ParameterDialog(QDialog):
    """Dialog for collecting query parameters with enhanced widgets"""
    
    # Signal emitted when parameters are confirmed
    parameters_confirmed = pyqtSignal(dict)
    
    def __init__(self, operation_name, parameters, parent=None):
        super().__init__(parent)
        self.operation_name = operation_name
        self.parameters = parameters
        self.parameter_widgets = {}
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Setup the parameter dialog UI - versão compacta"""
        self.setWindowTitle(f"Parâmetros - {self.operation_name}")
        self.setModal(True)
        self.setMinimumSize(380, 280)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title compacto
        title_label = QLabel(f"📋 {self.operation_name}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Parameters group compacto
        params_group = QGroupBox("Parâmetros")
        params_layout = QFormLayout(params_group)
        params_layout.setSpacing(8)
        params_layout.setContentsMargins(10, 15, 10, 10)
        
        # Create parameter input widgets using factory
        for param_name, param_config in self.parameters.items():
            param_type = param_config.get('type', 'text')
            param_label = param_config.get('label', param_name)
            
            label = QLabel(f"{param_label}:")
            label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 10px;")
            label.setToolTip(param_config.get('description', ''))
            
            widget = ParameterWidgetFactory.create_widget(param_config)
            
            self.parameter_widgets[param_name] = {
                'widget': widget,
                'type': param_type,
                'config': param_config
            }
            params_layout.addRow(label, widget)
        
        layout.addWidget(params_group)
        
        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # Buttons compactos
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(80, 30)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("✓ Executar")
        ok_btn.setFixedSize(100, 30)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_parameters)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Set focus to first parameter widget
        if self.parameter_widgets:
            first_widget_info = list(self.parameter_widgets.values())[0]
            first_widget = first_widget_info['widget']
            if hasattr(first_widget, 'setFocus'):
                first_widget.setFocus()
    
    def setup_styles(self):
        """Setup dialog styles - versão compacta"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dfe6e9;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: white;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #34495e;
                font-size: 10px;
            }
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #dfe6e9;
                border-color: #3498db;
            }
            QPushButton:default {
                background-color: #27ae60;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:default:hover {
                background-color: #229954;
            }
            QLabel {
                color: #2c3e50;
                font-size: 10px;
            }
        """)
    
    def accept_parameters(self):
        """Collect parameters and emit signal"""
        parameters = {}
        
        for param_name, widget_info in self.parameter_widgets.items():
            widget = widget_info['widget']
            param_type = widget_info['type']
            param_config = widget_info['config']
            
            # Usar factory para obter valor
            value = ParameterWidgetFactory.get_value(widget, param_type)
            
            # Validação para campos obrigatórios
            if param_config.get('required') and not value:
                from PyQt5.QtWidgets import QMessageBox
                param_label = param_config.get('label', param_name)
                msg = QMessageBox(self)
                msg.setWindowTitle("Campo Obrigatório")
                msg.setText(f"O campo '{param_label}' é obrigatório.")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                if hasattr(widget, 'setFocus'):
                    widget.setFocus()
                return
            
            # Validação para campos numéricos
            if param_type in ('number', 'number_slider'):
                min_val = param_config.get('min')
                if min_val is not None and value < min_val:
                    from PyQt5.QtWidgets import QMessageBox
                    param_label = param_config.get('label', param_name)
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Erro de Validação")
                    msg.setText(f"O campo '{param_label}' deve ser maior ou igual a {min_val}.")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    if hasattr(widget, 'setFocus'):
                        widget.setFocus()
                    return
            
            # Converter para string se necessário
            if param_type in ('number', 'number_slider', 'decimal'):
                parameters[param_name] = str(value)
            elif param_type == 'date_range':
                parameters['data_inicio'] = value['start']
                parameters['data_fim'] = value['end']
            else:
                parameters[param_name] = value
        
        # Emit signal with collected parameters
        self.parameters_confirmed.emit(parameters)
        self.accept()
    
    def get_parameters(self):
        """Get collected parameters (for synchronous usage)"""
        parameters = {}
        
        for param_name, widget_info in self.parameter_widgets.items():
            widget = widget_info['widget']
            param_type = widget_info['type']
            param_config = widget_info['config']
            
            value = ParameterWidgetFactory.get_value(widget, param_type)
            
            # Validação básica
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
    
    Args:
        operation_name: Name of the operation
        parameters: Dictionary defining parameter configuration
        parent: Parent widget
        
    Returns:
        dict: Collected parameters if OK clicked, None if cancelled
    """
    dialog = ParameterDialog(operation_name, parameters, parent)
    
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_parameters()
    
    return None