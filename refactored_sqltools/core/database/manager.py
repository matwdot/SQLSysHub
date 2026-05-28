"""
Database manager for handling multiple database drivers.

This module provides a central manager that implements the factory pattern
for creating and managing different database drivers.
"""

from typing import Dict, Any, Optional, Type, Sequence

from .drivers.base import DatabaseDriver, QueryResult
from .drivers.firebird import FirebirdDriver
from .drivers.sqlserver import SqlServerDriver
from ...utils.exceptions import ValidationError, ConnectionError
from ...utils.validators import validate_connection_params


class DatabaseManager:
    """
    Central manager for multiple database drivers.
    
    Implements the factory pattern to create appropriate drivers based on
    database type and manages connection state across different database types.
    """
    
    # Registry of available drivers
    _driver_registry: Dict[str, Type[DatabaseDriver]] = {
        'Firebird': FirebirdDriver,
        'SQL Server': SqlServerDriver,
    }
    
    def __init__(self):
        self._drivers: Dict[str, DatabaseDriver] = {}
        self._current_driver: Optional[DatabaseDriver] = None
        self._current_db_type: Optional[str] = None
    
    @classmethod
    def register_driver(cls, db_type: str, driver_class: Type[DatabaseDriver]) -> None:
        """
        Register a new database driver type.
        
        Args:
            db_type (str): Database type identifier
            driver_class (Type[DatabaseDriver]): Driver class to register
        """
        cls._driver_registry[db_type] = driver_class
    
    @classmethod
    def get_supported_databases(cls) -> list:
        """
        Get list of supported database types.
        
        Returns:
            list: List of supported database type names
        """
        return list(cls._driver_registry.keys())
    
    def get_driver(self, db_type: str) -> DatabaseDriver:
        """
        Get or create a driver for the specified database type.
        
        Args:
            db_type (str): Database type (e.g., 'Firebird', 'SQL Server')
            
        Returns:
            DatabaseDriver: Driver instance for the specified type
            
        Raises:
            ValidationError: If database type is not supported
        """
        if db_type not in self._driver_registry:
            supported = ', '.join(self._driver_registry.keys())
            raise ValidationError(
                f"Tipo de banco não suportado: {db_type}. "
                f"Tipos suportados: {supported}"
            )
        
        # Create driver if it doesn't exist
        if db_type not in self._drivers:
            driver_class = self._driver_registry[db_type]
            self._drivers[db_type] = driver_class()
        
        return self._drivers[db_type]
    
    def connect(self, db_type: str, **params) -> bool:
        """
        Connect to a database using the appropriate driver.
        
        Args:
            db_type (str): Database type
            **params: Database-specific connection parameters
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ValidationError: If database type is not supported
            ConnectionError: If connection fails
        """
        if db_type in ('Firebird', 'SQL Server'):
            validate_connection_params(db_type, **params)
        driver = self.get_driver(db_type)
        success = driver.connect(**params)
        
        if success:
            self._current_driver = driver
            self._current_db_type = db_type
        
        return success
    
    def disconnect(self, db_type: Optional[str] = None) -> None:
        """
        Disconnect from database(s).
        
        Args:
            db_type (Optional[str]): Specific database type to disconnect.
                                   If None, disconnects current driver.
        """
        if db_type:
            # Disconnect specific driver
            if db_type in self._drivers:
                self._drivers[db_type].disconnect()
                if self._current_db_type == db_type:
                    self._current_driver = None
                    self._current_db_type = None
        else:
            # Disconnect current driver
            if self._current_driver:
                self._current_driver.disconnect()
                self._current_driver = None
                self._current_db_type = None
    
    def disconnect_all(self) -> None:
        """Disconnect from all databases."""
        for driver in self._drivers.values():
            driver.disconnect()
        
        self._current_driver = None
        self._current_db_type = None
    
    def execute_query(
        self,
        query: str,
        db_type: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
    ) -> QueryResult:
        """
        Execute a query using the current or specified driver.
        
        Args:
            query (str): SQL query to execute
            db_type (Optional[str]): Database type to use. If None, uses current driver.
            
        Returns:
            QueryResult: Query execution results
            
        Raises:
            ConnectionError: If no driver is connected
            ValidationError: If specified database type is invalid
        """
        if db_type:
            driver = self.get_driver(db_type)
            if not driver.is_connected():
                raise ConnectionError(f"Não conectado ao banco {db_type}")
        else:
            if not self._current_driver:
                raise ConnectionError("Nenhuma conexão de banco disponível")
            driver = self._current_driver
        
        return driver.execute_query(query, params)
    
    def is_connected(self, db_type: Optional[str] = None) -> bool:
        """
        Check if connected to database.
        
        Args:
            db_type (Optional[str]): Database type to check. If None, checks current driver.
            
        Returns:
            bool: True if connected
        """
        if db_type:
            if db_type in self._drivers:
                return self._drivers[db_type].is_connected()
            return False
        else:
            return self._current_driver is not None and self._current_driver.is_connected()
    
    def get_current_driver_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current driver.
        
        Returns:
            Optional[Dict[str, Any]]: Driver information or None if no current driver
        """
        if not self._current_driver:
            return None
        
        info = {
            'database_type': self._current_db_type,
            'is_connected': self._current_driver.is_connected(),
            'connection_params': self._current_driver.get_connection_params()
        }
        
        # Add driver-specific info if available
        if hasattr(self._current_driver, 'get_driver_info'):
            info.update(self._current_driver.get_driver_info())
        
        return info
    
    def get_all_connections_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all driver connections.
        
        Returns:
            Dict[str, Dict[str, Any]]: Status information for each driver
        """
        status = {}
        
        for db_type, driver in self._drivers.items():
            status[db_type] = {
                'is_connected': driver.is_connected(),
                'connection_params': driver.get_connection_params(),
                'is_current': driver == self._current_driver
            }
            
            # Add driver-specific info if available
            if hasattr(driver, 'get_driver_info'):
                status[db_type].update(driver.get_driver_info())
        
        return status
    
    def switch_current_driver(self, db_type: str) -> bool:
        """
        Switch to a different connected driver as the current one.
        
        Args:
            db_type (str): Database type to switch to
            
        Returns:
            bool: True if switch successful
            
        Raises:
            ValidationError: If database type is not supported
            ConnectionError: If driver is not connected
        """
        driver = self.get_driver(db_type)
        
        if not driver.is_connected():
            raise ConnectionError(f"Driver para {db_type} não está conectado")
        
        self._current_driver = driver
        self._current_db_type = db_type
        return True
