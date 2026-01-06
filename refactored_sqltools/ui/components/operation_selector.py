"""
Operation Selector Component

Refactored to use the OperationRegistry from the core layer instead of
hardcoded operations. This maintains proper separation of concerns by
keeping business logic in the core layer and UI logic in the UI layer.

Parâmetros são exibidos inline na mesma sessão, sem popup.
Utiliza componentes aprimorados para entrada de parâmetros.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem,
                            QLineEdit, QDateEdit, QFormLayout, QPushButton, QFrame,
                            QSizePolicy, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt, QDate
from PyQt5.QtGui import QFont

from refactored_sqltools.core.operations.registry import operation_registry
from refactored_sqltools.ui.components.enhanced_parameters import (
    ParameterWidgetFactory, StyledDateEdit, EnhancedSpinBox, 
    EnhancedLineEdit, EnhancedComboBox, NumberWithSlider
)
from refactored_sqltools.config import get_config_manager


class OperationSelector(QWidget):
    """Reusable operation selector component that uses OperationRegistry"""
    
    # Signals
    operation_changed = pyqtSignal(str)  # operation_name
    sql_updated = pyqtSignal(str)  # sql_text
    parameters_requested = pyqtSignal(str, dict)  # operation_name, parameters_config (kept for compatibility)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_operation_name = None
        self.current_parameters = {}  # Store current parameters for queries with variables
        self.parameter_widgets = {}  # Store parameter input widgets
        self.parameters_config = {}  # Store current parameters configuration
        self.config = get_config_manager()
        self.setup_ui()
        self.setup_styles()
        self.load_operations()
    
    def setup_ui(self):
        """Setup the operation selector UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Operation selection group
        operation_group = QGroupBox("Selecione a Operação")
        operation_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        operation_layout = QVBoxLayout(operation_group)
        operation_layout.setContentsMargins(8, 12, 8, 8)
        operation_layout.setSpacing(4)
        
        # Filter checkboxes - more compact
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(2)
        
        filter_label = QLabel("Filtro:")
        filter_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        filter_layout.addWidget(filter_label)
        
        self.pdv_checkbox = QCheckBox("PDV")
        self.pdv_checkbox.setChecked(False)
        self.pdv_checkbox.stateChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.pdv_checkbox)
        
        self.server_checkbox = QCheckBox("Server")
        self.server_checkbox.setChecked(True)
        self.server_checkbox.stateChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.server_checkbox)
        
        self.ambos_checkbox = QCheckBox("Ambos")
        self.ambos_checkbox.setChecked(False)
        self.ambos_checkbox.stateChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.ambos_checkbox)
        
        filter_layout.addStretch()
        operation_layout.addLayout(filter_layout)
        
        # Operation tree widget for listing
        self.operation_tree = QTreeWidget()
        self.operation_tree.setHeaderHidden(True)
        self.operation_tree.setMinimumHeight(60)
        self.operation_tree.setMaximumHeight(120)
        self.operation_tree.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.operation_tree.itemClicked.connect(self.on_operation_changed)
        operation_layout.addWidget(self.operation_tree)
        
        # Operation description
        self.operation_description = QLabel()
        self.operation_description.setWordWrap(True)
        self.operation_description.setMinimumHeight(30)
        self.operation_description.setMaximumHeight(80)
        self.operation_description.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.operation_description.setStyleSheet("color: #7f8c8d; padding: 4px; font-style: italic; font-size: 10px;")
        self.operation_description.setOpenExternalLinks(True)  # Permite abrir links no navegador
        self.operation_description.setTextFormat(Qt.RichText)  # Suporta HTML
        operation_layout.addWidget(self.operation_description)
        
        # Parameters section (inline, no popup)
        self.parameters_frame = QFrame()
        self.parameters_frame.setFrameShape(QFrame.StyledPanel)
        self.parameters_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.parameters_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                margin-top: 2px;
            }
        """)
        self.parameters_layout = QVBoxLayout(self.parameters_frame)
        self.parameters_layout.setContentsMargins(6, 6, 6, 6)
        self.parameters_layout.setSpacing(4)
        
        # Parameters title
        self.parameters_title = QLabel("Parâmetros:")
        self.parameters_title.setStyleSheet("font-weight: bold; color: #34495e; font-size: 10px; border: none; background: transparent;")
        self.parameters_layout.addWidget(self.parameters_title)
        
        # Form layout for parameter inputs
        self.parameters_form = QFormLayout()
        self.parameters_form.setSpacing(4)
        self.parameters_form.setContentsMargins(0, 0, 0, 0)
        self.parameters_layout.addLayout(self.parameters_form)
        
        # Initially hide parameters section
        self.parameters_frame.setVisible(False)
        operation_layout.addWidget(self.parameters_frame)
        
        # Add stretch to push everything to the top
        operation_layout.addStretch()
        
        layout.addWidget(operation_group)
    
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
            QCheckBox {
                font-size: 10px;
                color: #2c3e50;
                spacing: 3px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #bdc3c7;
                border-radius: 2px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QTreeWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 2px;
                background-color: white;
                color: #2c3e50;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 3px 2px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #ebf5fb;
            }
            QTreeWidget:hover {
                border: 1px solid #3498db;
            }
            QLabel {
                font-size: 10px;
            }
        """)
    
    def on_filter_changed(self):
        """Handle filter checkbox changes"""
        self.load_operations()
    
    def get_selected_types(self):
        """Get list of selected operation types"""
        selected_types = []
        if self.pdv_checkbox.isChecked():
            selected_types.append('PDV')
        if self.server_checkbox.isChecked():
            selected_types.append('Server')
        if self.ambos_checkbox.isChecked():
            selected_types.append('Ambos')
        return selected_types
    
    def load_operations(self):
        """Load available operations from OperationRegistry filtered by type"""
        # Get selected operation types
        selected_types = self.get_selected_types()
        
        # Get operations organized by sessions from the registry, filtered by type
        operations_by_session = operation_registry.get_operations_by_type(selected_types)
        
        # Store current selection
        current_selection = None
        current_item = self.operation_tree.currentItem()
        if current_item:
            current_selection = current_item.data(0, Qt.UserRole)
        
        # Clear tree widget
        self.operation_tree.clear()
        
        # Collect all operations from all sessions (without session names)
        all_operations = []
        for session_name, operations in operations_by_session.items():
            for operation_name in operations.keys():
                all_operations.append(operation_name)
        
        # Sort operations alphabetically
        all_operations.sort()
        
        # Add operations directly to tree (no session grouping)
        for operation_name in all_operations:
            operation_item = QTreeWidgetItem(self.operation_tree)
            operation_item.setText(0, operation_name)
            operation_item.setData(0, Qt.UserRole, operation_name)
        
        # Try to restore previous selection
        if current_selection and current_selection in all_operations:
            self.set_operation(current_selection)
        else:
            # Try to restore last operation from config
            last_operation = self.config.get_last_operation()
            if last_operation and last_operation in all_operations:
                self.set_operation(last_operation)
            elif all_operations:
                # Select first operation if available
                first_item = self.operation_tree.topLevelItem(0)
                if first_item:
                    self.operation_tree.setCurrentItem(first_item)
                    self.on_operation_changed(first_item, 0)
    
    def on_operation_changed(self, item=None, column=None):
        """Handle operation selection change"""
        if item is None:
            item = self.operation_tree.currentItem()
        
        if not item:
            return
            
        # Get operation name from item data
        operation_name = item.data(0, Qt.UserRole)
        
        if not operation_name:
            return
        
        try:
            # Get operation from registry
            operation = operation_registry.get_operation(operation_name)
            self.current_operation_name = operation_name
            
            # Save last operation to config
            self.config.set_last_operation(operation_name)
            
            # Update description
            self.operation_description.setText(operation.description)
            
            # Check if operation has parameters
            if operation_registry.has_parameters(operation_name):
                # Get parameter configuration from registry
                self.parameters_config = operation_registry.get_operation_parameters(operation_name)
                # Show inline parameters
                self.show_inline_parameters(operation_name, self.parameters_config)
            else:
                # Clear any existing parameters and hide section
                self.current_parameters = {}
                self.parameters_config = {}
                self.hide_inline_parameters()
                # Update SQL immediately for operations without parameters
                self.update_sql()
            
            # Emit signal
            self.operation_changed.emit(operation_name)
            
        except KeyError:
            # Operation not found in registry
            self.operation_description.setText("Operação não encontrada no registry")
            self.hide_inline_parameters()
            return
    
    def show_inline_parameters(self, operation_name, parameters_config):
        """Show parameter inputs inline (no popup) using enhanced widgets"""
        # Clear existing parameter widgets
        self.clear_parameter_widgets()
        
        # Create parameter input widgets based on parameter types using factory
        for param_name, param_config in parameters_config.items():
            param_type = param_config.get('type', 'text')
            param_label = param_config.get('label', param_name)
            
            # Label compacto
            label = QLabel(f"{param_label}:")
            label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 10px; border: none; background: transparent;")
            label.setToolTip(param_config.get('description', ''))
            
            # Criar widget usando a factory
            widget = ParameterWidgetFactory.create_widget(param_config)
            
            # Armazenar widget e tipo para coleta posterior
            self.parameter_widgets[param_name] = {
                'widget': widget,
                'type': param_type,
                'config': param_config
            }
            
            self.parameters_form.addRow(label, widget)
        
        # Show parameters section
        self.parameters_frame.setVisible(True)
        
        # Set focus to first parameter widget
        if self.parameter_widgets:
            first_widget_info = list(self.parameter_widgets.values())[0]
            first_widget = first_widget_info['widget']
            if hasattr(first_widget, 'setFocus'):
                first_widget.setFocus()
    
    def hide_inline_parameters(self):
        """Hide the inline parameters section"""
        self.clear_parameter_widgets()
        self.parameters_frame.setVisible(False)
    
    def clear_parameter_widgets(self):
        """Clear all parameter input widgets"""
        # Remove all rows from form layout
        while self.parameters_form.count():
            item = self.parameters_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.parameter_widgets = {}
    
    def collect_parameters(self):
        """Collect parameters from inline widgets using factory"""
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
                return None
            
            # Validação para campos numéricos
            if param_type in ('number', 'number_slider'):
                if param_config.get('min') is not None and value < param_config['min']:
                    from PyQt5.QtWidgets import QMessageBox
                    param_label = param_config.get('label', param_name)
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Erro de Validação")
                    msg.setText(f"O campo '{param_label}' deve ser maior ou igual a {param_config['min']}.")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    if hasattr(widget, 'setFocus'):
                        widget.setFocus()
                    return None
            
            # Converter para string se necessário (para compatibilidade com SQL)
            if param_type in ('number', 'number_slider', 'decimal'):
                parameters[param_name] = str(value)
            elif param_type == 'date_range':
                # Expandir date_range em dois parâmetros
                parameters['data_inicio'] = value['start']
                parameters['data_fim'] = value['end']
            else:
                parameters[param_name] = value
        
        return parameters
    
    def update_sql(self):
        """Update and emit SQL text using the operation from registry"""
        if not self.current_operation_name:
            return
        
        try:
            operation = operation_registry.get_operation(self.current_operation_name)
            
            # Generate SQL using the operation
            if self.current_parameters:
                sql = operation.get_sql(**self.current_parameters)
            else:
                sql = operation.get_sql()
            
            # Add check SQL if available
            check_sql = operation.get_check_sql()
            if check_sql:
                sql = f"-- Verificação:\n{check_sql}\n\n-- Execução:\n{sql}"
            
            self.sql_updated.emit(sql)
            
        except Exception as e:
            # If there's an error generating SQL, emit empty string
            self.sql_updated.emit(f"-- Erro ao gerar SQL: {str(e)}")
    
    def set_parameters(self, parameters):
        """Set parameters collected from parameter dialog"""
        self.current_parameters = parameters
        self.update_sql()
    
    def get_current_operation(self):
        """Get current operation details from registry"""
        if not self.current_operation_name:
            return None
        
        try:
            operation = operation_registry.get_operation(self.current_operation_name)
            
            # Return operation details
            return {
                'name': self.current_operation_name,
                'description': operation.description,
                'operation_instance': operation,
                'parameters': self.current_parameters.copy()
            }
        except KeyError:
            return None
    
    def get_formatted_sql(self):
        """Get SQL formatted with current parameters using operation from registry"""
        if not self.current_operation_name:
            return ""
        
        try:
            operation = operation_registry.get_operation(self.current_operation_name)
            
            # Generate SQL using the operation
            if self.current_parameters:
                sql = operation.get_sql(**self.current_parameters)
            else:
                sql = operation.get_sql()
            
            return sql
            
        except Exception as e:
            return f"-- Erro ao gerar SQL: {str(e)}"
    
    def set_operation(self, operation_name):
        """Set current operation by name"""
        try:
            # Verify operation exists in registry
            operation_registry.get_operation(operation_name)
            
            # Find the operation item in the tree
            for i in range(self.operation_tree.topLevelItemCount()):
                operation_item = self.operation_tree.topLevelItem(i)
                if operation_item.data(0, Qt.UserRole) == operation_name:
                    self.operation_tree.setCurrentItem(operation_item)
                    self.on_operation_changed(operation_item, 0)
                    return
        except KeyError:
            # Operation not found in registry
            pass