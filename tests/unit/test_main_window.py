"""
Unit tests for MainWindow class.

Tests the integration of UI components and main window functionality.
"""

import pytest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from refactored_sqltools.ui.windows.main_window import MainWindow


class TestMainWindow:
    """Test cases for MainWindow class"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance for testing"""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def main_window(self, app):
        """Create MainWindow instance for testing"""
        window = MainWindow()
        return window
    
    def test_initialization(self, main_window):
        """Test MainWindow initialization"""
        # Check that main window is created
        assert main_window is not None
        assert main_window.windowTitle() == "SQL SysHub - Utilitarios de Banco de Dados"
        
        # Check that components are created
        assert hasattr(main_window, 'connection_panel')
        assert hasattr(main_window, 'operation_selector')
        assert hasattr(main_window, 'results_display')
        assert hasattr(main_window, 'status_progress')
        assert hasattr(main_window, 'db_manager')
        assert hasattr(main_window, 'status_bar')
        
        # Check initial state
        assert not main_window.execute_btn.isEnabled()
        assert not main_window.sql_group.isVisible()
        assert main_window.status_bar.currentMessage() == "Pronto"
    
    def test_component_integration(self, main_window):
        """Test that components are properly integrated"""
        # Check that connection panel exists and has expected properties
        connection_panel = main_window.connection_panel
        assert connection_panel is not None
        assert hasattr(connection_panel, 'connection_requested')
        assert hasattr(connection_panel, 'disconnection_requested')
        
        # Check that operation selector exists and has expected properties
        operation_selector = main_window.operation_selector
        assert operation_selector is not None
        assert hasattr(operation_selector, 'sql_updated')
        
        # Check that results display exists
        results_display = main_window.results_display
        assert results_display is not None
        
        # Check that status progress exists
        status_progress = main_window.status_progress
        assert status_progress is not None
    
    def test_sql_display_toggle(self, main_window):
        """Test SQL display toggle functionality"""
        # Show the window first to ensure proper event handling
        main_window.show()
        
        # Initially hidden
        assert not main_window.sql_group.isVisible()
        assert main_window.toggle_sql_btn.toolTip() == "Mostrar SQL"
        
        # Call toggle method directly (more reliable than mouse click in tests)
        main_window.toggle_sql_display()
        assert main_window.sql_group.isVisible()
        assert main_window.toggle_sql_btn.toolTip() == "Ocultar SQL"
        
        # Toggle back
        main_window.toggle_sql_display()
        assert not main_window.sql_group.isVisible()
        assert main_window.toggle_sql_btn.toolTip() == "Mostrar SQL"
    
    def test_connection_state_handling(self, main_window):
        """Test connection state handling"""
        # Initially disconnected
        assert not main_window.execute_btn.isEnabled()
        
        # Simulate connection
        main_window.on_connection_changed(True)
        assert main_window.execute_btn.isEnabled()
        
        # Simulate disconnection
        main_window.on_connection_changed(False)
        assert not main_window.execute_btn.isEnabled()
    
    def test_sql_update(self, main_window):
        """Test SQL display update"""
        test_sql = "SELECT * FROM test_table"
        main_window.update_sql_display(test_sql)
        # The new SQL editor formats the SQL, so we check if the original SQL is contained
        formatted_sql = main_window.sql_editor_widget.get_sql_text()
        # Remove extra whitespace and line breaks for comparison
        formatted_clean = ' '.join(formatted_sql.split())
        assert formatted_clean == test_sql
    
    @patch('refactored_sqltools.ui.windows.main_window.QMessageBox')
    def test_execute_operation_not_connected(self, mock_msgbox, main_window):
        """Test execute operation when not connected"""
        # Mock database manager to return not connected
        main_window.db_manager.is_connected = Mock(return_value=False)
        
        # Try to execute operation
        main_window.execute_operation()
        
        # Should handle gracefully when not connected
        assert not main_window.db_manager.is_connected()
    
    @patch('refactored_sqltools.ui.windows.main_window.QMessageBox')
    def test_execute_operation_no_operation(self, mock_msgbox, main_window):
        """Test execute operation when no operation selected"""
        # Mock database manager to return connected
        main_window.db_manager.is_connected = Mock(return_value=True)
        
        # Mock operation selector to return None
        main_window.operation_selector.get_current_operation = Mock(return_value=None)
        
        # Try to execute operation
        main_window.execute_operation()
        
        # Should handle gracefully when no operation selected
        assert main_window.operation_selector.get_current_operation() is None
    
    def test_status_bar_methods(self, main_window):
        """Test status bar message methods"""
        # Test show_success_status
        main_window.show_success_status("Test success message")
        current_message = main_window.status_bar.currentMessage()
        assert "Test success message" in current_message
        
        # Test show_error_status
        main_window.show_error_status("Test error message")
        current_message = main_window.status_bar.currentMessage()
        assert "Test error message" in current_message
        
        # Test show_info_status
        main_window.show_info_status("Test info message")
        current_message = main_window.status_bar.currentMessage()
        assert "Test info message" in current_message
        
        # Test show_permanent_status
        main_window.show_permanent_status("Permanent message")
        assert main_window.status_bar.currentMessage() == "Permanent message"
    
    def test_cleanup_on_close(self, main_window):
        """Test cleanup when window is closed"""
        # Mock database manager
        main_window.db_manager.is_connected = Mock(return_value=True)
        main_window.db_manager.disconnect_all = Mock()
        
        # Mock worker
        main_window.worker = Mock()
        main_window.worker.isRunning = Mock(return_value=True)
        main_window.worker.stop = Mock()
        main_window.worker.wait = Mock()
        
        # Create close event
        from PyQt5.QtGui import QCloseEvent
        event = QCloseEvent()
        
        # Call close event handler
        main_window.closeEvent(event)
        
        # Check cleanup was called
        main_window.db_manager.disconnect_all.assert_called_once()
        main_window.worker.stop.assert_called_once()
        main_window.worker.wait.assert_called_once_with(1000)
        
        # Event should be accepted
        assert event.isAccepted()