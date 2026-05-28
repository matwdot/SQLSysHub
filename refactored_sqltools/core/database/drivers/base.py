"""
Base interface for database drivers.

This module defines the abstract base class that all database drivers must implement,
ensuring consistent behavior across different database types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Sequence
from dataclasses import dataclass

from ....utils.exceptions import ConnectionError, QueryExecutionError


@dataclass
class QueryResult:
    """Represents the result of a database query execution."""
    success: bool
    message: str
    columns: Optional[List[str]] = None
    data: Optional[List[Tuple]] = None
    rows_affected: Optional[int] = None


class DatabaseDriver(ABC):
    """
    Abstract base class for database drivers.
    
    All database drivers must inherit from this class and implement
    the required methods to ensure consistent behavior across different
    database types.
    """
    
    def __init__(self):
        self._connection = None
        self._cursor = None
        self._is_connected = False
        self._connection_params = {}
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Establish connection to the database.
        
        Args:
            **kwargs: Database-specific connection parameters
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the database connection and clean up resources.
        
        This method should safely close the connection and cursor,
        and reset the connection state.
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Sequence[Any]] = None) -> QueryResult:
        """
        Execute a SQL query and return the results.
        
        Args:
            query (str): SQL query to execute
            params: Optional query parameters
            
        Returns:
            QueryResult: Object containing query results and metadata
            
        Raises:
            QueryExecutionError: If query execution fails
            ConnectionError: If not connected to database
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if the driver is currently connected to the database.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._is_connected
    
    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get the current connection parameters.
        
        Returns:
            Dict[str, Any]: Dictionary of connection parameters
        """
        return self._connection_params.copy()
    
    def _validate_connection(self) -> None:
        """
        Validate that the driver is connected before executing operations.
        
        Raises:
            ConnectionError: If not connected to database
        """
        if not self._is_connected:
            raise ConnectionError("Não conectado ao banco de dados")
    
    def _handle_query_result(self, query: str) -> QueryResult:
        """
        Process query results and return standardized QueryResult object.
        
        Args:
            query (str): The executed query
            
        Returns:
            QueryResult: Standardized result object
        """
        try:
            query_upper = query.strip().upper()
            
            # Check if it's a SELECT query (including CTEs that start with WITH)
            is_select_query = (query_upper.startswith('SELECT') or 
                             query_upper.startswith('WITH'))
            
            if is_select_query:
                # Handle SELECT queries (including CTEs)
                rows = self._cursor.fetchall()
                columns = [desc[0] for desc in self._cursor.description] if self._cursor.description else []
                
                return QueryResult(
                    success=True,
                    message=f"Query executada com sucesso. {len(rows)} linhas retornadas.",
                    columns=columns,
                    data=rows
                )
            else:
                # Handle INSERT, UPDATE, DELETE queries
                if hasattr(self._connection, 'commit'):
                    self._connection.commit()
                
                rows_affected = getattr(self._cursor, 'rowcount', 0)
                
                return QueryResult(
                    success=True,
                    message=f"Query executada com sucesso. {rows_affected} linhas afetadas.",
                    rows_affected=rows_affected
                )
                
        except Exception as e:
            # Rollback on error
            if hasattr(self._connection, 'rollback'):
                try:
                    self._connection.rollback()
                except Exception:
                    pass
            
            # Se já é uma QueryExecutionError, usar a mensagem diretamente
            if isinstance(e, QueryExecutionError):
                return QueryResult(
                    success=False,
                    message=str(e)
                )
            else:
                return QueryResult(
                    success=False,
                    message=f"Falha na execução da query: {str(e)}"
                )
