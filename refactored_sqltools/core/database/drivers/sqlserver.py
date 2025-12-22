"""
SQL Server database driver implementation.

This module provides the SQL Server-specific implementation of the DatabaseDriver
interface, using the pyodbc driver library.
"""

from typing import Dict, Any

from .base import DatabaseDriver, QueryResult
from ....utils.exceptions import ConnectionError, QueryExecutionError, DriverImportError


class SqlServerDriver(DatabaseDriver):
    """
    SQL Server database driver implementation.
    
    Uses pyodbc driver to connect to Microsoft SQL Server databases.
    Supports both local and remote SQL Server instances.
    """
    
    def __init__(self):
        super().__init__()
        self._driver_module = None
    
    def _import_driver(self):
        """
        Import the pyodbc driver for SQL Server.
        
        Returns:
            module: pyodbc module
            
        Raises:
            DriverImportError: If pyodbc is not available
        """
        try:
            import pyodbc
            return pyodbc
        except ImportError:
            raise DriverImportError(
                "Driver SQL Server não encontrado.\n\n"
                "Instale o driver com: pip install pyodbc"
            )
    
    def connect(self, host: str = "localhost", port: str = "1433", 
                username: str = "sa", password: str = "", 
                database: str = "master", **kwargs) -> bool:
        """
        Connect to SQL Server database.
        
        Args:
            host (str): Database host (default: localhost)
            port (str): Database port (default: 1433)
            username (str): Database username (default: sa)
            password (str): Database password
            database (str): Database name (default: master)
            **kwargs: Additional connection parameters
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
            DriverImportError: If pyodbc driver not available
        """
        try:
            # Import driver if not already done
            if not self._driver_module:
                self._driver_module = self._import_driver()
            
            # Store connection parameters
            self._connection_params = {
                'host': host,
                'port': port,
                'username': username,
                'database': database,
                'driver_name': 'pyodbc'
            }
            
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={host},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password}"
            )
            
            # Try alternative drivers if ODBC Driver 17 fails
            try:
                self._connection = self._driver_module.connect(conn_str)
            except Exception as e:
                # Try with ODBC Driver 13
                conn_str_alt = conn_str.replace("ODBC Driver 17", "ODBC Driver 13")
                try:
                    self._connection = self._driver_module.connect(conn_str_alt)
                except:
                    # Try with SQL Server Native Client
                    conn_str_native = conn_str.replace(
                        "ODBC Driver 17 for SQL Server", 
                        "SQL Server Native Client 11.0"
                    )
                    try:
                        self._connection = self._driver_module.connect(conn_str_native)
                    except:
                        # Re-raise original error
                        raise e
            
            self._cursor = self._connection.cursor()
            self._is_connected = True
            return True
            
        except Exception as e:
            self._is_connected = False
            self._connection = None
            self._cursor = None
            raise ConnectionError(f"Falha ao conectar ao banco SQL Server: {str(e)}")
    
    def disconnect(self) -> None:
        """
        Disconnect from SQL Server database and clean up resources.
        """
        try:
            if self._cursor:
                self._cursor.close()
            if self._connection:
                self._connection.close()
        except:
            # Ignore errors during cleanup
            pass
        finally:
            self._connection = None
            self._cursor = None
            self._is_connected = False
    
    def execute_query(self, query: str) -> QueryResult:
        """
        Execute SQL query on SQL Server database.
        
        Args:
            query (str): SQL query to execute
            
        Returns:
            QueryResult: Query execution results
            
        Raises:
            ConnectionError: If not connected to database
            QueryExecutionError: If query execution fails
        """
        self._validate_connection()
        
        try:
            self._cursor.execute(query)
            return self._handle_query_result(query)
            
        except Exception as e:
            # Rollback on error
            if self._connection:
                try:
                    self._connection.rollback()
                except:
                    pass
            
            raise QueryExecutionError(f"Falha na execução da query SQL Server: {str(e)}")
    
    def get_driver_info(self) -> Dict[str, Any]:
        """
        Get information about the current SQL Server driver.
        
        Returns:
            Dict[str, Any]: Driver information including name and version
        """
        info = {
            'driver_name': 'pyodbc',
            'database_type': 'SQL Server',
            'is_connected': self._is_connected
        }
        
        if self._driver_module:
            try:
                info['driver_version'] = self._driver_module.version
            except:
                pass
        
        return info
    
    def get_available_drivers(self) -> list:
        """
        Get list of available ODBC drivers for SQL Server.
        
        Returns:
            list: List of available driver names
        """
        if not self._driver_module:
            try:
                self._driver_module = self._import_driver()
            except DriverImportError:
                return []
        
        try:
            drivers = self._driver_module.drivers()
            sql_server_drivers = [
                driver for driver in drivers 
                if 'SQL Server' in driver or 'ODBC' in driver
            ]
            return sql_server_drivers
        except:
            return []