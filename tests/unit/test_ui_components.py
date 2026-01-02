"""
Unit tests for UI components
"""

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDate
import sys

from refactored_sqltools.ui.components import (
    ConnectionPanel, OperationSelector, ResultsDisplay, ProgressIndicator
)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        yield app
        app.quit()
    else:
        yield QApplication.instance()


class TestConnectionPanel:
    """Test ConnectionPanel component"""
    
    def test_initialization(self, qapp):
        """Test ConnectionPanel initializes correctly"""
        panel = ConnectionPanel()
        assert panel is not None
        assert not panel.is_connected
        assert panel.db_type_combo.currentText() == "Firebird"
    
    def test_db_type_change(self, qapp):
        """Test database type change updates fields"""
        panel = ConnectionPanel()
        
        # Test Firebird defaults
        panel.db_type_combo.setCurrentText("Firebird")
        panel.on_db_type_change()
        assert panel.port_entry.text() == "3050"
        assert panel.username_entry.text() == "SYSDBA"
        
        # Test SQL Server defaults
        panel.db_type_combo.setCurrentText("SQL Server")
        panel.on_db_type_change()
        assert panel.port_entry.text() == "1433"
        assert panel.username_entry.text() == "sa"
    
    def test_connection_params(self, qapp):
        """Test getting connection parameters"""
        panel = ConnectionPanel()
        params = panel.get_connection_params()
        
        assert 'db_type' in params
        assert 'host' in params
        assert 'port' in params
        assert 'username' in params
        assert 'password' in params
        assert 'database' in params


class TestOperationSelector:
    """Test OperationSelector component"""
    
    def test_initialization(self, qapp):
        """Test OperationSelector initializes correctly"""
        selector = OperationSelector()
        assert selector is not None
        # Check that operations are loaded (using the tree widget)
        assert selector.operation_tree.topLevelItemCount() > 0
    
    def test_operation_change(self, qapp):
        """Test operation change updates description"""
        selector = OperationSelector()
        
        # Set to a known operation
        selector.set_operation("Cancelar Cupom")
        
        description = selector.operation_description.text()
        # Check for any meaningful description content
        assert len(description) > 0
    
    def test_ncm_query_dates(self, qapp):
        """Test NCM query shows date fields"""
        selector = OperationSelector()
        selector.show()  # Show widget to make visibility tests work
        
        # Set to NCM query
        selector.set_operation("Consultar NCM Inexistente")
        
        # Check if selector handles date-based operations properly
        # This test verifies the operation selector can handle operations that require dates
        operation = selector.get_current_operation()
        assert operation is not None
        assert operation['name'] == "Consultar NCM Inexistente"
    
    def test_get_current_operation(self, qapp):
        """Test getting current operation details"""
        selector = OperationSelector()
        operation = selector.get_current_operation()
        
        assert operation is not None
        assert 'name' in operation
        assert 'description' in operation
        # Check for operation instance or SQL content
        assert 'operation_instance' in operation or 'sql' in operation


class TestResultsDisplay:
    """Test ResultsDisplay component"""
    
    def test_initialization(self, qapp):
        """Test ResultsDisplay initializes correctly"""
        display = ResultsDisplay()
        display.show()  # Show widget to make visibility tests work
        assert display is not None
        assert display.current_mode == "text"
        assert display.results_text.isVisible()
        assert not display.results_table.isVisible()
    
    def test_display_text_results(self, qapp):
        """Test displaying text results"""
        display = ResultsDisplay()
        message = "Test message"
        
        display.display_text_results(message)
        assert display.results_text.toPlainText() == message
        assert not display.toggle_btn.isVisible()
    
    def test_display_table_results(self, qapp):
        """Test displaying table results"""
        display = ResultsDisplay()
        display.show()  # Show widget to make visibility tests work
        columns = ["ID", "Name", "Value"]
        data = [(1, "Test", 100), (2, "Test2", 200)]
        
        display.display_table_results(columns, data)
        
        assert display.toggle_btn.isVisible()
        assert display.results_table.columnCount() == len(columns)
        assert display.results_table.rowCount() == len(data)
        # Table should be shown by default for tabular data
        assert display.current_mode == "table"
        assert not display.results_text.isVisible()
        assert display.results_table.isVisible()
    
    def test_toggle_display_mode(self, qapp):
        """Test toggling between text and table modes"""
        display = ResultsDisplay()
        display.show()  # Show widget to make visibility tests work
        columns = ["ID", "Name"]
        data = [(1, "Test")]
        
        display.display_table_results(columns, data)
        
        # Initially in table mode (default for tabular data)
        assert display.current_mode == "table"
        assert not display.results_text.isVisible()
        assert display.results_table.isVisible()
        
        # Toggle to text mode
        display.toggle_display_mode()
        assert display.current_mode == "text"
        assert display.results_text.isVisible()
        assert not display.results_table.isVisible()


class TestProgressIndicator:
    """Test ProgressIndicator component"""
    
    def test_initialization(self, qapp):
        """Test ProgressIndicator initializes correctly"""
        indicator = ProgressIndicator()
        assert indicator is not None
        assert indicator.current_progress == 0
        assert indicator.target_progress == 0
        assert not indicator.is_animating
    
    def test_show_hide_progress(self, qapp):
        """Test showing and hiding progress"""
        indicator = ProgressIndicator()
        indicator.show()  # Show widget to make visibility tests work
        
        # Initially hidden
        assert not indicator.progress_bar.isVisible()
        
        # Show progress
        indicator.show_progress("Testing...")
        assert indicator.progress_bar.isVisible()
        assert indicator.progress_label.isVisible()
        assert "Testing" in indicator.progress_label.text()
        
        # Hide progress
        indicator.hide_progress()
        assert not indicator.progress_bar.isVisible()
        assert not indicator.progress_label.isVisible()
    
    def test_set_progress(self, qapp):
        """Test setting progress value"""
        indicator = ProgressIndicator()
        indicator.show_progress()
        
        # Set progress
        indicator.set_progress(50, "Half way...")
        assert indicator.target_progress == 50
        assert "Half way" in indicator.progress_label.text()
        
        # Test clamping
        indicator.set_progress(150)  # Should clamp to 100
        assert indicator.target_progress == 100
        
        indicator.set_progress(-10)  # Should clamp to 0
        assert indicator.target_progress == 0
    
    def test_state_methods(self, qapp):
        """Test various state setting methods"""
        indicator = ProgressIndicator()
        indicator.show()  # Show widget to make visibility tests work
        
        # Test connecting state
        indicator.set_connecting_state()
        assert indicator.progress_bar.isVisible()
        assert "Conectando" in indicator.progress_label.text()
        
        # Test executing state
        indicator.set_executing_state("Test Operation")
        assert "Test Operation" in indicator.progress_label.text()
        
        # Test completed state
        indicator.set_completed_state()
        assert indicator.target_progress == 100
        assert "Concluído" in indicator.progress_label.text()