"""
Operation Selector Component

Refactored to use the OperationRegistry from the core layer instead of
hardcoded operations. This maintains proper separation of concerns by
keeping business logic in the core layer and UI logic in the UI layer.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt

from refactored_sqltools.core.operations.registry import operation_registry


class OperationSelector(QWidget):
    """Reusable operation selector component that uses OperationRegistry"""
    
    # Signals
    operation_changed = pyqtSignal(str)  # operation_name
    sql_updated = pyqtSignal(str)  # sql_text
    parameters_requested = pyqtSignal(str, dict)  # operation_name, parameters_config
    execute_requested = pyqtSignal()  # request automatic execution
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_operation_name = None
        self.current_parameters = {}  # Store current parameters for queries with variables
        self.setup_ui()
        self.setup_styles()
        self.load_operations()
    
    def setup_ui(self):
        """Setup the operation selector UI"""
        layout = QVBoxLayout(self)
        
        # Operation selection group
        operation_group = QGroupBox("Selecione a Operação")
        operation_layout = QVBoxLayout(operation_group)
        
        # Filter checkboxes
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar por tipo:"))
        
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
        
        filter_layout.addStretch()  # Push checkboxes to the left
        operation_layout.addLayout(filter_layout)
        
        # Operation tree widget for listing
        self.operation_tree = QTreeWidget()
        self.operation_tree.setHeaderHidden(True)
        self.operation_tree.itemClicked.connect(self.on_operation_changed)
        operation_layout.addWidget(self.operation_tree)
        
        # Operation description
        self.operation_description = QLabel()
        self.operation_description.setWordWrap(True)
        self.operation_description.setStyleSheet("color: #7f8c8d; padding: 8px; font-style: italic; font-size: 11px;")
        operation_layout.addWidget(self.operation_description)
        
        layout.addWidget(operation_group)
    
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
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #34495e;
                font-size: 13px;
            }
            QCheckBox {
                font-size: 12px;
                color: #2c3e50;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
                border-color: #2980b9;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QComboBox, QTreeWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #2c3e50;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 12px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #41aaf0;
                color: white;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 12px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #41aaf0;
            }
            QComboBox:hover, QTreeWidget:hover {
                border: 1px solid #3498db;
            }
            QLabel {
                font-size: 12px;
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
            # Select first operation if available
            if all_operations:
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
            
            # Update description
            self.operation_description.setText(operation.description)
            
            # Check if operation has parameters
            if operation_registry.has_parameters(operation_name):
                # Get parameter configuration from registry
                parameters_config = operation_registry.get_operation_parameters(operation_name)
                # Emit signal to request parameters from parent
                self.parameters_requested.emit(operation_name, parameters_config)
            else:
                # Clear any existing parameters
                self.current_parameters = {}
                # Update SQL immediately for operations without parameters
                self.update_sql()
            
            # Emit signal
            self.operation_changed.emit(operation_name)
            
        except KeyError:
            # Operation not found in registry
            self.operation_description.setText("Operação não encontrada no registry")
            return
    
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
        
        # Emit signal to request automatic execution
        if parameters:  # Only if parameters were actually provided (not cancelled)
            self.execute_requested.emit()
    
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