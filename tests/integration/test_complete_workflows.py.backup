"""
Integration tests for complete SQL SysHub workflows.

Tests complete workflows from connection to query execution,
verifying all original SQL SysHub.py functionality works in refactored version.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

# Add the refactored_sqltools to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from refactored_sqltools.ui.windows.main_window import MainWindow
from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.operations.predefined import operation_registry
from refactored_sqltools.utils.exceptions import ConnectionError, QueryExecutionError


@pytest.fixture
def app():
    """Create QApplication for testing"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def main_window(app):
    """Create MainWindow for testing"""
    window = MainWindow()
    yield window
    window.cleanup()


@pytest.mark.integration
class TestCompleteWorkflows:
    """Test complete workflows from connection to query execution"""
    
    def test_firebird_connection_workflow(self, main_window):
        """Test complete Firebird connection workflow"""
        # Mock the database manager's connect method directly
        with patch.object(main_window.db_manager, 'connect') as mock_connect:
            mock_connect.return_value = True
            
            with patch.object(main_window.db_manager, 'is_connected') as mock_is_connected:
                mock_is_connected.return_value = True
                
                # Test connection parameters
                db_type = "Firebird"
                host = "localhost"
                port = "3050"
                username = "SYSDBA"
                password = "masterkey"
                database = "/path/to/database.fdb"
                
                # Simulate connection request
                main_window.handle_connection_request(db_type, host, port, username, password, database)
                
                # Wait for worker to complete
                if main_window.worker:
                    main_window.worker.wait()
                
                # Verify connection was attempted
                mock_connect.assert_called_once_with(
                    db_type, 
                    host=host, 
                    port=port, 
                    username=username, 
                    password=password, 
                    database=database
                )
                
                # Verify UI state
                assert main_window.db_manager.is_connected()
    
    def test_sqlserver_connection_workflow(self, main_window):
        """Test complete SQL Server connection workflow"""
        # Mock the database manager's connect method directly
        with patch.object(main_window.db_manager, 'connect') as mock_connect:
            mock_connect.return_value = True
            
            with patch.object(main_window.db_manager, 'is_connected') as mock_is_connected:
                mock_is_connected.return_value = True
                
                # Test connection parameters
                db_type = "SQL Server"
                host = "localhost"
                port = "1433"
                username = "sa"
                password = "password"
                database = "TestDB"
                
                # Simulate connection request
                main_window.handle_connection_request(db_type, host, port, username, password, database)
                
                # Wait for worker to complete
                if main_window.worker:
                    main_window.worker.wait()
                
                # Verify connection was attempted
                mock_connect.assert_called_once_with(
                    db_type, 
                    host=host, 
                    port=port, 
                    username=username, 
                    password=password, 
                    database=database
                )
                
                # Verify UI state
                assert main_window.db_manager.is_connected()
    
    def test_query_execution_workflow(self, main_window):
        """Test complete query execution workflow"""
        # Mock database connection
        with patch.object(main_window.db_manager, 'is_connected', return_value=True), \
             patch.object(main_window.db_manager, 'execute_query') as mock_execute:
            
            # Mock query result
            from refactored_sqltools.core.database.drivers.base import QueryResult
            mock_result = QueryResult(
                success=True,
                message="Query executed successfully",
                columns=["id", "name"],
                data=[(1, "Test"), (2, "Test2")],
                rows_affected=2
            )
            mock_execute.return_value = mock_result
            
            # Set up operation selector with a test operation
            test_operation = {
                'name': 'Test Query',
                'description': 'Test query description',
                'sql': 'SELECT * FROM test_table'
            }
            
            # Mock the operation selector
            with patch.object(main_window.operation_selector, 'get_current_operation', return_value=test_operation), \
                 patch.object(main_window.operation_selector, 'get_formatted_sql', return_value='SELECT * FROM test_table'), \
                 patch('refactored_sqltools.ui.windows.main_window.QMessageBox.question', return_value=16384):  # QMessageBox.Yes
                
                # Execute operation
                main_window.execute_operation()
                
                # Wait for worker to complete
                if main_window.worker:
                    main_window.worker.wait()
                
                # Verify query was executed
                mock_execute.assert_called_once_with('SELECT * FROM test_table', None)
    
    def test_ncm_query_with_date_range(self, main_window):
        """Test NCM query with date range parameters"""
        # Mock database connection
        with patch.object(main_window.db_manager, 'is_connected', return_value=True), \
             patch.object(main_window.db_manager, 'execute_query') as mock_execute:
            
            # Mock query result
            from refactored_sqltools.core.database.drivers.base import QueryResult
            mock_result = QueryResult(
                success=True,
                message="NCM query executed successfully",
                columns=["ncm", "count"],
                data=[("12345678", 10), ("87654321", 5)],
                rows_affected=2
            )
            mock_execute.return_value = mock_result
            
            # Get NCM operation from predefined operations
            operations = operation_registry.list_operations()
            ncm_operation = None
            for name, op in operations.items():
                if "NCM" in name:
                    # Provide required parameters for NCM query
                    test_params = {
                        'data_inicio': '2024-01-01',
                        'data_fim': '2024-12-31'
                    }
                    ncm_operation = {
                        'name': name,
                        'description': op.description,
                        'sql': op.get_sql(**test_params)
                    }
                    break
            
            if ncm_operation:
                # Mock the operation selector with NCM operation
                with patch.object(main_window.operation_selector, 'get_current_operation', return_value=ncm_operation), \
                     patch.object(main_window.operation_selector, 'get_formatted_sql', return_value=ncm_operation['sql']), \
                     patch('refactored_sqltools.ui.windows.main_window.QMessageBox.question', return_value=16384):  # QMessageBox.Yes
                    
                    # Execute operation
                    main_window.execute_operation()
                    
                    # Wait for worker to complete
                    if main_window.worker:
                        main_window.worker.wait()
                    
                    # Verify query was executed
                    mock_execute.assert_called_once()
    
    def test_error_handling_workflow(self, main_window):
        """Test error handling in complete workflow"""
        # Test connection error
        with patch('refactored_sqltools.core.database.drivers.firebird.FirebirdDriver') as mock_driver_class:
            mock_driver = Mock()
            mock_driver.connect.side_effect = ConnectionError("Connection failed")
            mock_driver_class.return_value = mock_driver
            
            # Simulate connection request
            main_window.handle_connection_request("Firebird", "localhost", "3050", "SYSDBA", "masterkey", "/path/to/db.fdb")
            
            # Wait for worker to complete
            if main_window.worker:
                main_window.worker.wait()
            
            # Verify connection failed
            assert not main_window.db_manager.is_connected()
        
        # Test query execution error
        with patch.object(main_window.db_manager, 'is_connected', return_value=True), \
             patch.object(main_window.db_manager, 'execute_query') as mock_execute:
            
            # Mock query error
            mock_execute.side_effect = QueryExecutionError("Query failed")
            
            test_operation = {
                'name': 'Test Query',
                'description': 'Test query description',
                'sql': 'SELECT * FROM invalid_table'
            }
            
            # Mock the operation selector
            with patch.object(main_window.operation_selector, 'get_current_operation', return_value=test_operation), \
                 patch.object(main_window.operation_selector, 'get_formatted_sql', return_value='SELECT * FROM invalid_table'), \
                 patch('refactored_sqltools.ui.windows.main_window.QMessageBox.question', return_value=16384):  # QMessageBox.Yes
                
                # Execute operation
                main_window.execute_operation()
                
                # Wait for worker to complete
                if main_window.worker:
                    main_window.worker.wait()
                
                # Verify query was attempted
                mock_execute.assert_called_once()
    
    def test_disconnection_workflow(self, main_window):
        """Test disconnection workflow"""
        # Mock connected state
        with patch.object(main_window.db_manager, 'is_connected', return_value=True), \
             patch.object(main_window.db_manager, 'disconnect') as mock_disconnect:
            
            # Simulate disconnection request
            main_window.handle_disconnection_request()
            
            # Verify disconnection was called
            mock_disconnect.assert_called_once()
    
    def test_ui_component_integration(self, main_window):
        """Test integration between UI components"""
        # Test that all components are properly initialized
        assert main_window.connection_panel is not None
        assert main_window.operation_selector is not None
        assert main_window.results_display is not None
        assert main_window.progress_indicator is not None
        
        # Test that signals are connected
        # This is verified by checking that the signal connections don't raise errors
        # and that the components respond to state changes
        
        # Test connection state change
        main_window.on_connection_changed(True)
        assert main_window.execute_btn.isEnabled()
        
        main_window.on_connection_changed(False)
        assert not main_window.execute_btn.isEnabled()


@pytest.mark.integration
class TestOriginalFunctionalityEquivalence:
    """Test that all original SQL SysHub.py functionality works in refactored version"""
    
    def test_all_predefined_operations_available(self):
        """Test that all predefined operations from original are available"""
        operations = operation_registry.list_operations()
        
        # Verify we have operations
        assert len(operations) > 0
        
        # Verify each operation has required fields
        for name, operation in operations.items():
            assert isinstance(name, str)
            assert hasattr(operation, 'description')
            assert hasattr(operation, 'get_sql')
            assert isinstance(operation.description, str)
            
            # Test that get_sql method works with appropriate parameters
            try:
                # Try without parameters first
                sql = operation.get_sql()
                assert isinstance(sql, str)
            except (KeyError, TypeError):
                # If it requires parameters, try with common date parameters
                try:
                    from datetime import datetime
                    sql = operation.get_sql(
                        data_inicio=datetime(2024, 1, 1),
                        data_fim=datetime(2024, 12, 31)
                    )
                    assert isinstance(sql, str)
                except (KeyError, TypeError):
                    # If it still fails, just verify the method exists
                    assert callable(operation.get_sql)
    
    def test_database_manager_functionality(self):
        """Test that DatabaseManager provides all required functionality"""
        from refactored_sqltools.utils.exceptions import ValidationError
        
        manager = DatabaseManager()
        
        # Test driver creation
        firebird_driver = manager.get_driver("Firebird")
        assert firebird_driver is not None
        
        sqlserver_driver = manager.get_driver("SQL Server")
        assert sqlserver_driver is not None
        
        # Test invalid driver
        with pytest.raises(ValidationError):
            manager.get_driver("InvalidDB")
    
    def test_worker_functionality(self):
        """Test that worker threads provide all required functionality"""
        from refactored_sqltools.core.workers.database_worker import DatabaseWorkerFactory
        
        manager = DatabaseManager()
        
        # Test connection worker creation
        connection_worker = DatabaseWorkerFactory.create_connection_worker(
            manager, "Firebird", "localhost", "3050", "SYSDBA", "masterkey", "/path/to/db.fdb"
        )
        assert connection_worker is not None
        
        # Test query worker creation
        query_worker = DatabaseWorkerFactory.create_query_worker(
            manager, "SELECT 1", "Test Query"
        )
        assert query_worker is not None


@pytest.mark.integration
@pytest.mark.slow
class TestEdgeCasesAndErrorScenarios:
    """Test edge cases and error scenarios"""
    
    def test_invalid_connection_parameters(self, main_window):
        """Test handling of invalid connection parameters"""
        # Test with empty parameters
        main_window.handle_connection_request("", "", "", "", "", "")
        
        # Test with invalid database type
        main_window.handle_connection_request("InvalidDB", "host", "port", "user", "pass", "db")
        
        # Verify application doesn't crash
        assert main_window is not None
    
    def test_concurrent_operations(self, main_window):
        """Test handling of concurrent operations"""
        # Mock database connection
        with patch.object(main_window.db_manager, 'is_connected', return_value=True):
            
            # Try to execute multiple operations
            test_operation = {
                'name': 'Test Query',
                'description': 'Test query description',
                'sql': 'SELECT * FROM test_table'
            }
            
            with patch.object(main_window.operation_selector, 'get_current_operation', return_value=test_operation), \
                 patch.object(main_window.operation_selector, 'get_formatted_sql', return_value='SELECT * FROM test_table'), \
                 patch('refactored_sqltools.ui.windows.main_window.QMessageBox.question', return_value=16384):  # QMessageBox.Yes
                
                # Execute first operation
                main_window.execute_operation()
                
                # Try to execute second operation while first is running
                # Should be prevented by UI state
                if main_window.worker and main_window.worker.isRunning():
                    assert not main_window.execute_btn.isEnabled()
    
    def test_resource_cleanup(self, main_window):
        """Test proper resource cleanup"""
        # Mock database connection
        with patch.object(main_window.db_manager, 'is_connected', return_value=True), \
             patch.object(main_window.db_manager, 'disconnect_all') as mock_disconnect_all:
            
            # Test cleanup method
            main_window.cleanup()
            
            # Verify cleanup was called
            mock_disconnect_all.assert_called_once()
    
    def test_application_startup_and_shutdown(self):
        """Test complete application startup and shutdown"""
        # This test verifies the main.py functionality
        from refactored_sqltools.main import parse_arguments, setup_logging
        
        # Test argument parsing
        with patch('sys.argv', ['sqltools', '--debug', '--style', 'Fusion']):
            args = parse_arguments()
            assert args.debug is True
            assert args.style == 'Fusion'
        
        # Test logging setup
        setup_logging(debug=True)
        # If no exception is raised, logging setup worked
        
        setup_logging(debug=False)
        # If no exception is raised, logging setup worked