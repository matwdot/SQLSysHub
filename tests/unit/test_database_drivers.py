"""
Consolidated unit tests for database drivers functionality.

This file consolidates database driver tests, removing redundant
tests while maintaining essential functionality coverage.
"""

import pytest
from unittest.mock import Mock, patch
from refactored_sqltools.core.database.drivers.base import DatabaseDriver, QueryResult
from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.utils.exceptions import ValidationError, ConnectionError


class MockDatabaseDriver(DatabaseDriver):
    """Mock implementation of DatabaseDriver for testing."""
    
    def __init__(self):
        super().__init__()
        self.should_connect = True
        self.should_fail_query = False
    
    def connect(self, **kwargs) -> bool:
        if self.should_connect:
            self._is_connected = True
            self._connection = "mock_connection"
            self._cursor = "mock_cursor"
            self._connection_params = kwargs
            return True
        else:
            raise ConnectionError("Mock connection failed")
    
    def disconnect(self) -> None:
        self._is_connected = False
        self._connection = None
        self._cursor = None
    
    def execute_query(self, query: str) -> QueryResult:
        if not self._is_connected:
            return QueryResult(
                success=False,
                message='Not connected to database'
            )
        
        if self.should_fail_query:
            raise Exception("Mock query execution failed")
        
        # Simulate different query types
        query_upper = query.strip().upper()
        if query_upper.startswith('SELECT'):
            return QueryResult(
                success=True,
                message='Query executed successfully',
                columns=['test_column'],
                data=[('test_value',)],
                rows_affected=None
            )
        else:
            return QueryResult(
                success=True,
                message='Query executed successfully',
                columns=None,
                data=None,
                rows_affected=1
            )


class TestDatabaseDriverBase:
    """Test base database driver functionality."""
    
    def test_driver_connection_lifecycle(self):
        """Test complete driver connection lifecycle."""
        driver = MockDatabaseDriver()
        
        # Initially not connected
        assert not driver.is_connected()
        assert driver._connection is None
        
        # Connect
        result = driver.connect(host='localhost', database='test')
        assert result is True
        assert driver.is_connected()
        assert driver._connection == "mock_connection"
        
        # Check connection params are stored
        params = driver.get_connection_params()
        assert params['host'] == 'localhost'
        assert params['database'] == 'test'
        
        # Disconnect
        driver.disconnect()
        assert not driver.is_connected()
        assert driver._connection is None
    
    def test_driver_query_execution(self):
        """Test driver query execution functionality."""
        driver = MockDatabaseDriver()
        
        # Query without connection should fail
        result = driver.execute_query("SELECT 1")
        assert result.success is False
        assert 'Not connected' in result.message
        
        # Connect and test SELECT query
        driver.connect()
        result = driver.execute_query("SELECT * FROM test")
        assert result.success is True
        assert result.columns == ['test_column']
        assert result.data == [('test_value',)]
        assert result.rows_affected is None
        
        # Test UPDATE query
        result = driver.execute_query("UPDATE test SET value = 1")
        assert result.success is True
        assert result.columns is None
        assert result.data is None
        assert result.rows_affected == 1
    
    def test_driver_error_handling(self):
        """Test driver error handling."""
        driver = MockDatabaseDriver()
        
        # Test connection failure
        driver.should_connect = False
        with pytest.raises(ConnectionError):
            driver.connect()
        
        # Test query execution failure
        driver.should_connect = True
        driver.should_fail_query = True
        driver.connect()
        
        with pytest.raises(Exception):
            driver.execute_query("SELECT 1")
    
    def test_driver_validation_helper(self):
        """Test driver validation helper methods."""
        driver = MockDatabaseDriver()
        
        # Test validation when not connected
        with pytest.raises(ConnectionError):
            driver._validate_connection()
        
        # Test validation when connected
        driver.connect()
        driver._validate_connection()  # Should not raise


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_manager_driver_creation(self):
        """Test database manager driver creation."""
        manager = DatabaseManager()
        
        # Test Firebird driver creation
        firebird_driver = manager.get_driver("Firebird")
        assert firebird_driver is not None
        assert hasattr(firebird_driver, 'connect')
        assert hasattr(firebird_driver, 'disconnect')
        assert hasattr(firebird_driver, 'execute_query')
        
        # Test SQL Server driver creation
        sqlserver_driver = manager.get_driver("SQL Server")
        assert sqlserver_driver is not None
        assert hasattr(sqlserver_driver, 'connect')
        
        # Test driver caching (same instance returned)
        firebird_driver2 = manager.get_driver("Firebird")
        assert firebird_driver is firebird_driver2
    
    def test_manager_supported_databases(self):
        """Test manager supported databases functionality."""
        manager = DatabaseManager()
        
        supported = manager.get_supported_databases()
        assert 'Firebird' in supported
        assert 'SQL Server' in supported
        assert len(supported) >= 2
    
    def test_manager_error_handling(self):
        """Test manager error handling."""
        manager = DatabaseManager()
        
        # Test invalid database type
        with pytest.raises(ValidationError):
            manager.get_driver("InvalidDatabase")
        
        # Test error message contains supported types
        try:
            manager.get_driver("MySQL")
        except ValidationError as e:
            assert "Firebird" in str(e)
            assert "SQL Server" in str(e)
    
    def test_manager_connection_workflow(self):
        """Test manager connection workflow with mocked drivers."""
        manager = DatabaseManager()
        
        # Mock the driver creation to return our mock
        with patch.object(manager, 'get_driver') as mock_get_driver:
            mock_driver = MockDatabaseDriver()
            mock_get_driver.return_value = mock_driver
            
            # Test connection
            success = manager.connect("Firebird", host="localhost", 
                                    database="/path/to/db.fdb")
            
            assert success is True
            assert manager.is_connected()
            
            # Test disconnection
            manager.disconnect()
            assert not manager.is_connected()
    
    def test_manager_query_execution(self):
        """Test manager query execution workflow."""
        manager = DatabaseManager()
        
        with patch.object(manager, 'get_driver') as mock_get_driver:
            mock_driver = MockDatabaseDriver()
            mock_driver.connect()  # Pre-connect the mock
            mock_get_driver.return_value = mock_driver
            
            # Set up manager state
            manager._connected = True
            manager._current_driver = mock_driver
            
            # Test query execution
            result = manager.execute_query("SELECT * FROM test")
            
            assert result is not None
            assert result.success is True
            assert result.columns == ['test_column']
            assert result.data == [('test_value',)]


class TestSpecificDrivers:
    """Test specific driver implementations."""
    
    def test_firebird_driver_import_handling(self):
        """Test Firebird driver import handling."""
        from refactored_sqltools.core.database.drivers.firebird import FirebirdDriver
        
        driver = FirebirdDriver()
        
        # Test driver info
        info = driver.get_driver_info()
        assert info['database_type'] == 'Firebird'
        assert 'driver_name' in info
        assert 'is_connected' in info
    
    def test_sqlserver_driver_import_handling(self):
        """Test SQL Server driver import handling."""
        from refactored_sqltools.core.database.drivers.sqlserver import SqlServerDriver
        
        driver = SqlServerDriver()
        
        # Test driver info
        info = driver.get_driver_info()
        assert info['database_type'] == 'SQL Server'
        assert info['driver_name'] == 'pyodbc'
        assert 'is_connected' in info
    
    def test_driver_connection_parameters(self):
        """Test driver connection parameter handling."""
        from refactored_sqltools.core.database.drivers.firebird import FirebirdDriver
        from refactored_sqltools.core.database.drivers.sqlserver import SqlServerDriver
        
        # Test Firebird parameters
        fb_driver = FirebirdDriver()
        # Should not crash when testing parameter validation
        assert hasattr(fb_driver, 'connect')
        
        # Test SQL Server parameters
        sql_driver = SqlServerDriver()
        # Should not crash when testing parameter validation
        assert hasattr(sql_driver, 'connect')
        
        # Test available drivers method for SQL Server
        if hasattr(sql_driver, 'get_available_drivers'):
            drivers = sql_driver.get_available_drivers()
            assert isinstance(drivers, list)