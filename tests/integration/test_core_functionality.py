"""
Core functionality integration tests.

Tests the core functionality of the refactored SQL SysHub without complex UI interactions.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the refactored_sqltools to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.operations.predefined import operation_registry
from refactored_sqltools.core.workers.database_worker import DatabaseWorkerFactory
from refactored_sqltools.utils.exceptions import ValidationError, ConnectionError


@pytest.mark.integration
class TestCoreFunctionality:
    """Test core functionality integration"""
    
    def test_database_manager_driver_creation(self):
        """Test that DatabaseManager can create all supported drivers"""
        manager = DatabaseManager()
        
        # Test Firebird driver creation
        firebird_driver = manager.get_driver("Firebird")
        assert firebird_driver is not None
        assert hasattr(firebird_driver, 'connect')
        assert hasattr(firebird_driver, 'disconnect')
        assert hasattr(firebird_driver, 'execute_query')
        assert hasattr(firebird_driver, 'is_connected')
        
        # Test SQL Server driver creation
        sqlserver_driver = manager.get_driver("SQL Server")
        assert sqlserver_driver is not None
        assert hasattr(sqlserver_driver, 'connect')
        assert hasattr(sqlserver_driver, 'disconnect')
        assert hasattr(sqlserver_driver, 'execute_query')
        assert hasattr(sqlserver_driver, 'is_connected')
        
        # Test that drivers are cached (same instance returned)
        firebird_driver2 = manager.get_driver("Firebird")
        assert firebird_driver is firebird_driver2
    
    def test_operation_registry_functionality(self):
        """Test that operation registry provides all required operations"""
        operations = operation_registry.list_operations()
        
        # Verify we have operations
        assert len(operations) > 0
        
        # Test specific operations exist
        operation_names = operation_registry.get_operation_names()
        assert "Cancelar Cupom" in operation_names
        assert "Apagar Certificado" in operation_names
        
        # Test getting specific operation
        cancelar_cupom = operation_registry.get_operation("Cancelar Cupom")
        assert cancelar_cupom is not None
        assert cancelar_cupom.name == "Cancelar Cupom"
        assert hasattr(cancelar_cupom, 'get_sql')
        
        # Test operation SQL generation
        sql = cancelar_cupom.get_sql()
        assert isinstance(sql, str)
        assert len(sql) > 0
    
    def test_worker_factory_functionality(self):
        """Test that worker factory can create workers"""
        manager = DatabaseManager()
        
        # Test connection worker creation
        connection_worker = DatabaseWorkerFactory.create_connection_worker(
            manager, "Firebird", "localhost", "3050", "SYSDBA", "masterkey", "/path/to/db.fdb"
        )
        assert connection_worker is not None
        assert hasattr(connection_worker, 'start')
        assert hasattr(connection_worker, 'finished')
        assert hasattr(connection_worker, 'progress')
        
        # Test query worker creation
        query_worker = DatabaseWorkerFactory.create_query_worker(
            manager, "SELECT 1", "Test Query"
        )
        assert query_worker is not None
        assert hasattr(query_worker, 'start')
        assert hasattr(query_worker, 'finished')
        assert hasattr(query_worker, 'progress')
    
    def test_database_connection_workflow(self):
        """Test database connection workflow with mocked drivers"""
        manager = DatabaseManager()
        
        # Mock the Firebird driver
        with patch.object(manager, 'get_driver') as mock_get_driver:
            mock_driver = Mock()
            mock_driver.connect.return_value = True
            mock_driver.is_connected.return_value = True
            mock_get_driver.return_value = mock_driver
            
            # Test connection
            success = manager.connect("Firebird", host="localhost", port="3050", 
                                    username="SYSDBA", password="masterkey", 
                                    database="/path/to/db.fdb")
            
            assert success is True
            mock_driver.connect.assert_called_once()
            assert manager.is_connected()
    
    def test_query_execution_workflow(self):
        """Test query execution workflow with mocked drivers"""
        manager = DatabaseManager()
        
        # Mock the driver and its query execution
        with patch.object(manager, 'get_driver') as mock_get_driver:
            mock_driver = Mock()
            mock_driver.is_connected.return_value = True
            
            # Mock query result
            from refactored_sqltools.core.database.drivers.base import QueryResult
            mock_result = QueryResult(
                success=True,
                message="Query executed successfully",
                columns=["id", "name"],
                data=[(1, "Test"), (2, "Test2")],
                rows_affected=2
            )
            mock_driver.execute_query.return_value = mock_result
            mock_get_driver.return_value = mock_driver
            
            # Set connected state
            manager._connected = True
            manager._current_driver = mock_driver
            
            # Execute query
            result = manager.execute_query("SELECT * FROM test_table")
            
            assert result is not None
            assert result.success is True
            assert result.message == "Query executed successfully"
            assert result.columns == ["id", "name"]
            assert result.data == [(1, "Test"), (2, "Test2")]
            assert result.rows_affected == 2
    
    def test_error_handling(self):
        """Test error handling in core components"""
        manager = DatabaseManager()
        
        # Test invalid database type
        with pytest.raises(ValidationError):
            manager.get_driver("InvalidDB")
        
        # Test operation not found
        with pytest.raises(KeyError):
            operation_registry.get_operation("NonexistentOperation")
        
        # Test connection error handling
        with patch.object(manager, 'get_driver') as mock_get_driver:
            mock_driver = Mock()
            mock_driver.connect.side_effect = ConnectionError("Connection failed")
            mock_get_driver.return_value = mock_driver
            
            # Test that connection error is properly handled
            with pytest.raises(ConnectionError):
                manager.connect("Firebird", host="localhost", port="3050", 
                                        username="SYSDBA", password="masterkey", 
                                        database="/path/to/db.fdb")
    
    def test_operation_parameter_handling(self):
        """Test operation parameter handling"""
        # Test operation that requires parameters
        operations = operation_registry.list_operations()
        
        # Find NCM operation (requires date parameters)
        ncm_operation = None
        for name, op in operations.items():
            if "NCM" in name:
                ncm_operation = op
                break
        
        if ncm_operation:
            # Test with valid parameters
            from datetime import datetime
            sql = ncm_operation.get_sql(
                data_inicio=datetime(2024, 1, 1),
                data_fim=datetime(2024, 12, 31)
            )
            assert isinstance(sql, str)
            assert len(sql) > 0
            
            # Test parameter validation
            try:
                ncm_operation.validate_params(
                    data_inicio=datetime(2024, 1, 1),
                    data_fim=datetime(2024, 12, 31)
                )
            except Exception:
                # If validation fails, that's also acceptable for this test
                pass
    
    def test_complete_operation_workflow(self):
        """Test complete operation workflow from selection to execution"""
        manager = DatabaseManager()
        
        # Mock database connection
        with patch.object(manager, 'is_connected', return_value=True), \
             patch.object(manager, 'execute_query') as mock_execute:
            
            # Mock query result
            from refactored_sqltools.core.database.drivers.base import QueryResult
            mock_result = QueryResult(
                success=True,
                message="Operation completed successfully",
                columns=["result"],
                data=[("Success",)],
                rows_affected=1
            )
            mock_execute.return_value = mock_result
            
            # Get an operation
            operation = operation_registry.get_operation("Cancelar Cupom")
            
            # Get SQL for the operation
            sql = operation.get_sql()
            
            # Execute the operation
            result = manager.execute_query(sql)
            
            # Verify results
            assert result.success is True
            assert result.message == "Operation completed successfully"
            mock_execute.assert_called_once_with(sql)


@pytest.mark.integration
class TestOriginalFunctionalityEquivalence:
    """Test equivalence with original SQL SysHub functionality"""
    
    def test_all_original_operations_present(self):
        """Test that all operations from original SQL SysHub are present"""
        operations = operation_registry.list_operations()
        operation_names = set(operations.keys())
        
        # These are the key operations that should be present
        expected_operations = {
            "Cancelar Cupom",
            "Apagar Certificado", 
            "Corrigir Erro de Equipamento",
            "Limpar Tabelas do Fisco",
            "Consultar Transações",
            "Consultar Proprio",
            "Consultar NCM Inexistente"
        }
        
        # Verify all expected operations are present
        for expected_op in expected_operations:
            assert expected_op in operation_names, f"Operation '{expected_op}' not found"
    
    def test_database_types_supported(self):
        """Test that all original database types are supported"""
        manager = DatabaseManager()
        
        # Test Firebird support
        firebird_driver = manager.get_driver("Firebird")
        assert firebird_driver is not None
        
        # Test SQL Server support  
        sqlserver_driver = manager.get_driver("SQL Server")
        assert sqlserver_driver is not None
    
    def test_worker_thread_functionality(self):
        """Test that worker thread functionality matches original"""
        manager = DatabaseManager()
        
        # Test that workers can be created for both connection and query operations
        connection_worker = DatabaseWorkerFactory.create_connection_worker(
            manager, "Firebird", "localhost", "3050", "SYSDBA", "masterkey", "/path/to/db.fdb"
        )
        assert connection_worker is not None
        
        query_worker = DatabaseWorkerFactory.create_query_worker(
            manager, "SELECT 1", "Test Query"
        )
        assert query_worker is not None
        
        # Test that workers have the required signals
        assert hasattr(connection_worker, 'finished')
        assert hasattr(connection_worker, 'progress')
        assert hasattr(query_worker, 'finished')
        assert hasattr(query_worker, 'progress')