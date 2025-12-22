"""
Firebird database driver implementation.

This module provides the Firebird-specific implementation of the DatabaseDriver
interface, handling both fdb and firebirdsql driver libraries.
"""

import os
from typing import Dict, Any

from .base import DatabaseDriver, QueryResult
from ....utils.exceptions import ConnectionError, QueryExecutionError, DriverImportError


class FirebirdDriver(DatabaseDriver):
    """
    Firebird database driver implementation.
    
    Supports both fdb and firebirdsql driver libraries with automatic fallback.
    Handles local and remote Firebird database connections.
    """
    
    def __init__(self):
        super().__init__()
        self._driver_module = None
        self._driver_name = None
    
    def _import_driver(self):
        """
        Import the appropriate Firebird driver.
        
        Tries firebirdsql first (recommended), then falls back to fdb.
        
        Returns:
            tuple: (driver_name, driver_module)
            
        Raises:
            DriverImportError: If no Firebird driver is available
        """
        drivers_to_try = [
            ('firebirdsql', 'pip install firebirdsql'),
            ('fdb', 'pip install fdb'),
        ]
        
        for driver_name, install_cmd in drivers_to_try:
            try:
                if driver_name == 'fdb':
                    import fdb
                    return ('fdb', fdb)
                elif driver_name == 'firebirdsql':
                    import firebirdsql
                    return ('firebirdsql', firebirdsql)
            except ImportError:
                continue
        
        raise DriverImportError(
            "Nenhum driver Firebird encontrado.\n\n"
            "Instale um dos drivers:\n"
            "• pip install firebirdsql (Recomendado)\n"
            "• pip install fdb"
        )
    
    def connect(self, host: str = "localhost", port: str = "3050", 
                username: str = "SYSDBA", password: str = "masterkey", 
                database: str = "", **kwargs) -> bool:
        """
        Connect to Firebird database.
        
        Args:
            host (str): Database host (default: localhost)
            port (str): Database port (default: 3050)
            username (str): Database username (default: SYSDBA)
            password (str): Database password (default: masterkey)
            database (str): Database path or name
            **kwargs: Additional connection parameters
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ConnectionError: If connection fails
            DriverImportError: If no Firebird driver available
        """
        try:
            # Import driver if not already done
            if not self._driver_module:
                self._driver_name, self._driver_module = self._import_driver()
            
            # Validate database path for local connections
            if host.lower() in ['localhost', '127.0.0.1', '']:
                if not database or not os.path.exists(database):
                    raise ConnectionError(
                        f"Arquivo de banco de dados não encontrado: {database}\n\n"
                        "Verifique o caminho e tente novamente."
                    )
            
            # Store connection parameters
            self._connection_params = {
                'host': host,
                'port': port,
                'username': username,
                'database': database,
                'driver_name': self._driver_name
            }
            
            # Build connection based on driver type
            if self._driver_name == 'firebirdsql':
                self._connection = self._driver_module.connect(
                    host=host if host.lower() not in ['localhost', '127.0.0.1', ''] else 'localhost',
                    port=int(port) if port else 3050,
                    database=database,
                    user=username,
                    password=password,
                    charset='UTF8'
                )
            else:  # fdb driver
                # Build DSN for fdb
                if host.lower() in ['localhost', '127.0.0.1', '']:
                    dsn = database
                else:
                    dsn = f"{host}/{port}:{database}" if port != "3050" else f"{host}:{database}"
                
                self._connection = self._driver_module.connect(
                    dsn=dsn,
                    user=username,
                    password=password,
                    charset='UTF8'
                )
            
            self._cursor = self._connection.cursor()
            self._is_connected = True
            return True
            
        except Exception as e:
            self._is_connected = False
            self._connection = None
            self._cursor = None
            raise ConnectionError(f"Falha ao conectar ao banco Firebird: {str(e)}")
    
    def disconnect(self) -> None:
        """
        Disconnect from Firebird database and clean up resources.
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
        Execute SQL query on Firebird database.
        
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
            
            raise QueryExecutionError(f"Falha na execução da query Firebird: {str(e)}")
    
    def get_driver_info(self) -> Dict[str, Any]:
        """
        Get information about the current Firebird driver.
        
        Returns:
            Dict[str, Any]: Driver information including name and version
        """
        info = {
            'driver_name': self._driver_name,
            'database_type': 'Firebird',
            'is_connected': self._is_connected
        }
        
        if self._driver_module:
            try:
                if hasattr(self._driver_module, '__version__'):
                    info['driver_version'] = self._driver_module.__version__
            except:
                pass
        
        return info