"""
Parameter Dialog

Dialog window for collecting query parameters from user.
Opens as a separate window when queries have variables.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QDateEdit, QLineEdit, QFormLayout,
                            QGroupBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class ParameterDialog(QDialog):
    """Dialog for collecting query parameters"""
    
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
        """Setup the parameter dialog UI"""
        self.setWindowTitle(f"Parâmetros - {self.operation_name}")
        self.setModal(True)
        self.setFixedSize(420, 320)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(f"Informe os parâmetros para:")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Operation name
        operation_label = QLabel(self.operation_name)
        operation_font = QFont()
        operation_font.setPointSize(11)
        operation_label.setFont(operation_font)
        operation_label.setAlignment(Qt.AlignCenter)
        operation_label.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        layout.addWidget(operation_label)
        
        # Info message
        info_label = QLabel("A query será executada automaticamente após confirmar os parâmetros")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px; font-style: italic; margin-bottom: 15px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Parameters group
        params_group = QGroupBox("Parâmetros")
        params_layout = QFormLayout(params_group)
        params_layout.setSpacing(10)
        
        # Create parameter input widgets based on parameter types
        for param_name, param_config in self.parameters.items():
            param_type = param_config.get('type', 'text')
            param_label = param_config.get('label', param_name)
            param_default = param_config.get('default')
            
            label = QLabel(f"{param_label}:")
            
            if param_type == 'date':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                if param_default:
                    if param_default == 'today':
                        widget.setDate(QDate.currentDate())
                    elif param_default == 'month_ago':
                        widget.setDate(QDate.currentDate().addDays(-30))
                    else:
                        widget.setDate(QDate.fromString(param_default, "yyyy-MM-dd"))
                else:
                    widget.setDate(QDate.currentDate())
            else:  # text type
                widget = QLineEdit()
                if param_default:
                    widget.setText(str(param_default))
                widget.setPlaceholderText(param_config.get('placeholder', ''))
            
            self.parameter_widgets[param_name] = widget
            params_layout.addRow(label, widget)
        
        layout.addWidget(params_group)
        
        # Spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(100, 35)
        cancel_btn.clicked.connect(self.reject)
        
        # OK button
        ok_btn = QPushButton("Executar Query")
        ok_btn.setFixedSize(120, 35)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_parameters)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Set focus to first parameter widget
        if self.parameter_widgets:
            first_widget = list(self.parameter_widgets.values())[0]
            first_widget.setFocus()
    
    def setup_styles(self):
        """Setup dialog styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #34495e;
                font-size: 12px;
            }
            QLineEdit, QDateEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
                min-height: 20px;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
            QLineEdit:hover, QDateEdit:hover {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:default {
                background-color: #27ae60;
                font-weight: bold;
            }
            QPushButton:default:hover {
                background-color: #229954;
            }
            QPushButton:default:pressed {
                background-color: #1e8449;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                min-width: 100px;
            }
        """)
    
    def accept_parameters(self):
        """Collect parameters and emit signal"""
        parameters = {}
        
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QDateEdit):
                parameters[param_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QLineEdit):
                value = widget.text().strip()
                
                # Basic validation for numeric fields (pagination)
                if param_name in ['registros_por_pagina', 'pagina']:
                    try:
                        num_value = int(value) if value else 0
                        if num_value <= 0:
                            # Show error message
                            from PyQt5.QtWidgets import QMessageBox
                            msg = QMessageBox(self)
                            msg.setWindowTitle("Erro de Validação")
                            msg.setText(f"O campo '{self.parameters[param_name].get('label', param_name)}' deve ser um número maior que zero.")
                            msg.setIcon(QMessageBox.Warning)
                            msg.exec_()
                            widget.setFocus()
                            return
                    except ValueError:
                        # Show error message
                        from PyQt5.QtWidgets import QMessageBox
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Erro de Validação")
                        msg.setText(f"O campo '{self.parameters[param_name].get('label', param_name)}' deve conter apenas números.")
                        msg.setIcon(QMessageBox.Warning)
                        msg.exec_()
                        widget.setFocus()
                        return
                
                parameters[param_name] = value
        
        # Emit signal with collected parameters
        self.parameters_confirmed.emit(parameters)
        self.accept()
    
    def get_parameters(self):
        """Get collected parameters (for synchronous usage)"""
        parameters = {}
        
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QDateEdit):
                parameters[param_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QLineEdit):
                value = widget.text().strip()
                
                # Basic validation for numeric fields (pagination)
                if param_name in ['registros_por_pagina', 'pagina']:
                    try:
                        num_value = int(value) if value else 0
                        if num_value <= 0:
                            return None  # Invalid parameters
                    except ValueError:
                        return None  # Invalid parameters
                
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