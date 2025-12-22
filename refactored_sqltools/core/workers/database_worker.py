"""
Database worker thread for asynchronous database operations.

This module provides a worker thread implementation that handles database
operations asynchronously, with proper progress reporting, error handling,
and resource cleanup.
"""

from typing import Any, Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal

from ..database.manager import DatabaseManager
from ..database.drivers.base import QueryResult
from ...utils.exceptions import SQLSysHubException, ConnectionError, QueryExecutionError


class DatabaseWorker(QThread):
    """
    Worker thread for executing database operations asynchronously.
    
    This class handles database operations in a separate thread to prevent
    UI blocking, with proper progress reporting and error handling.
    
    Signals:
        finished: Emitted when operation completes (success: bool, message: str, result: Any)
        progress: Emitted during operation progress (value: int)
        error: Emitted when an error occurs (error_message: str)
    """
    
    # Signals for communication with main thread
    finished = pyqtSignal(bool, str, object)  # success, message, result
    progress = pyqtSignal(int)  # progress value (0-100)
    error = pyqtSignal(str)  # error message
    
    def __init__(self, db_manager: DatabaseManager, operation: str, 
                 operation_name: str, *args, **kwargs):
        """
        Initialize the database worker.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            operation (str): Operation type ('connect', 'execute_query', 'disconnect')
            operation_name (str): Human-readable operation name for logging
            *args: Operation-specific arguments
            **kwargs: Operation-specific keyword arguments
        """
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.operation_name = operation_name
        self.args = args
        self.kwargs = kwargs
        self._cleanup_required = False
    
    def run(self) -> None:
        """
        Execute the database operation in the worker thread.
        
        This method runs in a separate thread and handles different types
        of database operations with proper error handling and progress reporting.
        """
        try:
            self.progress.emit(10)  # Initial progress
            
            if self.operation == 'connect':
                self._handle_connect_operation()
            elif self.operation == 'execute_query':
                self._handle_execute_query_operation()
            elif self.operation == 'disconnect':
                self._handle_disconnect_operation()
            else:
                raise ValueError(f"Operação desconhecida: {self.operation}")
                
        except SQLSysHubException as e:
            self.progress.emit(100)
            self.error.emit(str(e))
            self.finished.emit(False, str(e), None)
        except Exception as e:
            self.progress.emit(100)
            error_msg = f"Erro inesperado em {self.operation_name}: {str(e)}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg, None)
        finally:
            self._cleanup_resources()
    
    def _handle_connect_operation(self) -> None:
        """
        Handle database connection operation.
        
        Expected args: (db_type, host, port, username, password, database)
        """
        if len(self.args) < 6:
            raise ValueError("Operação de conexão requer 6 argumentos: db_type, host, port, username, password, database")
        
        db_type, host, port, username, password, database = self.args[:6]
        
        self.progress.emit(30)
        
        # Prepare connection parameters
        connection_params = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'database': database
        }
        
        self.progress.emit(50)
        
        try:
            # Attempt connection
            success = self.db_manager.connect(db_type, **connection_params)
            
            self.progress.emit(90)
            
            if success:
                self.progress.emit(100)
                message = f"Conectado com sucesso ao banco: {db_type}"
                self.finished.emit(True, message, None)
            else:
                self.progress.emit(100)
                message = f"Falha ao conectar ao banco: {db_type}"
                self.finished.emit(False, message, None)
                
        except ConnectionError as e:
            self.progress.emit(100)
            # Usar a mensagem de erro diretamente do driver
            self.finished.emit(False, str(e), None)
    
    def _handle_execute_query_operation(self) -> None:
        """
        Handle query execution operation.
        
        Expected args: (query,) and optional kwargs: (db_type,)
        """
        if len(self.args) < 1:
            raise ValueError("Operação de execução de query requer pelo menos 1 argumento: query")
        
        query = self.args[0]
        db_type = self.kwargs.get('db_type', None)
        
        self.progress.emit(20)
        
        try:
            # Check connection
            if not self.db_manager.is_connected(db_type):
                db_name = db_type if db_type else "current database"
                raise ConnectionError(f"Não conectado ao {db_name}")
            
            self.progress.emit(40)
            
            # Execute query
            result = self.db_manager.execute_query(query, db_type)
            
            self.progress.emit(80)
            
            if result.success:
                self.progress.emit(100)
                self.finished.emit(True, result.message, result)
            else:
                self.progress.emit(100)
                self.finished.emit(False, result.message, result)
                
        except (ConnectionError, QueryExecutionError) as e:
            self.progress.emit(100)
            # Usar a mensagem de erro diretamente do driver, sem adicionar prefixo duplicado
            self.finished.emit(False, str(e), None)
    
    def _handle_disconnect_operation(self) -> None:
        """
        Handle database disconnection operation.
        
        Optional args: (db_type,) - if not provided, disconnects current driver
        """
        db_type = self.args[0] if self.args else None
        
        self.progress.emit(50)
        
        try:
            if db_type:
                self.db_manager.disconnect(db_type)
                message = f"Desconectado do {db_type}."
            else:
                self.db_manager.disconnect()
                message = "Desconectado do banco de dados."
            
            self.progress.emit(100)
            self.finished.emit(True, message, None)
            
        except Exception as e:
            self.progress.emit(100)
            message = f"Falha ao desconectar: {str(e)}"
            self.finished.emit(False, message, None)
    
    def _cleanup_resources(self) -> None:
        """
        Clean up any resources used by the worker thread.
        
        This method ensures proper cleanup of resources even if
        the operation fails or is interrupted.
        """
        try:
            # Mark cleanup as completed
            self._cleanup_required = False
            
            # Additional cleanup can be added here if needed
            # For example, closing temporary files, clearing caches, etc.
            
        except Exception as e:
            # Log cleanup errors but don't propagate them
            # as the main operation may have succeeded
            print(f"Aviso: Erro de limpeza no DatabaseWorker: {e}")
    
    def stop(self) -> None:
        """
        Request the worker to stop its current operation.
        
        This method provides a way to gracefully stop the worker thread
        if needed, though database operations should generally be allowed
        to complete.
        """
        if self.isRunning():
            self.requestInterruption()
            self._cleanup_required = True
    
    def get_operation_info(self) -> dict:
        """
        Get information about the current operation.
        
        Returns:
            dict: Dictionary containing operation details
        """
        return {
            'operation': self.operation,
            'operation_name': self.operation_name,
            'args_count': len(self.args),
            'kwargs_count': len(self.kwargs),
            'is_running': self.isRunning(),
            'cleanup_required': self._cleanup_required
        }


class DatabaseWorkerFactory:
    """
    Factory class for creating DatabaseWorker instances.
    
    This factory provides convenient methods for creating workers
    for common database operations.
    """
    
    @staticmethod
    def create_connection_worker(db_manager: DatabaseManager, db_type: str,
                               host: str, port: str, username: str, 
                               password: str, database: str) -> DatabaseWorker:
        """
        Create a worker for database connection operation.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            db_type (str): Database type
            host (str): Database host
            port (str): Database port
            username (str): Database username
            password (str): Database password
            database (str): Database name
            
        Returns:
            DatabaseWorker: Configured worker for connection operation
        """
        return DatabaseWorker(
            db_manager, 'connect', f'Connect to {db_type}',
            db_type, host, port, username, password, database
        )
    
    @staticmethod
    def create_query_worker(db_manager: DatabaseManager, query: str,
                          operation_name: str = "Execute Query",
                          db_type: Optional[str] = None) -> DatabaseWorker:
        """
        Create a worker for query execution operation.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            query (str): SQL query to execute
            operation_name (str): Human-readable operation name
            db_type (Optional[str]): Database type (uses current if None)
            
        Returns:
            DatabaseWorker: Configured worker for query execution
        """
        kwargs = {'db_type': db_type} if db_type else {}
        return DatabaseWorker(
            db_manager, 'execute_query', operation_name,
            query, **kwargs
        )
    
    @staticmethod
    def create_disconnect_worker(db_manager: DatabaseManager,
                               db_type: Optional[str] = None) -> DatabaseWorker:
        """
        Create a worker for database disconnection operation.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            db_type (Optional[str]): Database type (disconnects current if None)
            
        Returns:
            DatabaseWorker: Configured worker for disconnection operation
        """
        args = (db_type,) if db_type else ()
        operation_name = f'Disconnect from {db_type}' if db_type else 'Disconnect'
        
        return DatabaseWorker(
            db_manager, 'disconnect', operation_name, *args
        )