"""
Unit tests for DatabaseDriver base class.
"""

import pytest
from abc import ABC
from refactored_sqltools.core.database.drivers.base import DatabaseDriver, QueryResult


class MockDatabaseDriver(DatabaseDriver):
    """Mock implementation of DatabaseDriver for testing."""
    
    def __init__(self):
        super().__init__()
    
    def connect(self, **kwargs) -> bool:
        self._is_connected = True
        self._connection = "mock_connection"
        self._cursor = "mock_cursor"
        return True
    
    def disconnect(self) -> None:
        self._is_connected = False
        self._connection = None
        self._cursor = None
    
    def execute_query(self, query: str, params=None) -> QueryResult:
        if not self._is_connected:
            return QueryResult(
                success=False,
                message='Not connected to database'
            )
        return QueryResult(
            success=True,
            message='Query executed successfully',
            columns=['test_column'],
            data=[('test_value',)],
            rows_affected=1
        )


class TestDatabaseDriverBase:
    """Test cases for DatabaseDriver base class."""
    
    def test_database_driver_is_abstract(self):
        """Test that DatabaseDriver cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DatabaseDriver()
    
    def test_mock_driver_initialization(self):
        """Test that mock driver initializes correctly."""
        driver = MockDatabaseDriver()
        assert not driver.is_connected()
        assert driver.get_connection() is None
    
    def test_mock_driver_connection_cycle(self):
        """Test connection and disconnection cycle."""
        driver = MockDatabaseDriver()
        
        # Initially not connected
        assert not driver.is_connected()
        
        # Connect
        result = driver.connect(host='localhost', database='test')
        assert result is True
        assert driver.is_connected()
        
        # Disconnect
        driver.disconnect()
        assert not driver.is_connected()
    
    def test_mock_driver_query_execution(self):
        """Test query execution with mock driver."""
        driver = MockDatabaseDriver()
        
        # Query without connection should fail
        result = driver.execute_query("SELECT 1")
        assert result.success is False
        assert 'Not connected' in result.message
        
        # Connect and query should succeed
        driver.connect()
        result = driver.execute_query("SELECT 1")
        assert result.success is True
        assert result.columns == ['test_column']
        assert result.data == [('test_value',)]
        assert result.rows_affected == 1