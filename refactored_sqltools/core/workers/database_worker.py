"""
Database worker thread for asynchronous database operations.
"""

import logging
from typing import Any, Optional

from PyQt5.QtCore import QThread, pyqtSignal

from ..database.manager import DatabaseManager
from ...utils.exceptions import ConnectionError, QueryExecutionError, SQLSysHubException


logger = logging.getLogger(__name__)


class DatabaseWorker(QThread):
    """Worker thread for database operations."""

    finished = pyqtSignal(bool, str, object)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, db_manager: DatabaseManager, operation: str, operation_name: str, *args, **kwargs):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.operation_name = operation_name
        self.args = args
        self.kwargs = kwargs
        self._cleanup_required = False
        self._local_db_manager = None

    def run(self) -> None:
        try:
            self.progress.emit(10)

            if self.operation == "connect":
                self._handle_connect_operation()
            elif self.operation == "execute_query":
                self._handle_execute_query_operation()
            elif self.operation == "custom_operation":
                self._handle_custom_operation()
            elif self.operation == "disconnect":
                self._handle_disconnect_operation()
            else:
                raise ValueError(f"Operacao desconhecida: {self.operation}")
        except SQLSysHubException as exc:
            self.progress.emit(100)
            self.error.emit(str(exc))
            self.finished.emit(False, str(exc), None)
        except Exception as exc:
            self.progress.emit(100)
            error_msg = f"Erro inesperado em {self.operation_name}: {exc}"
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg, None)
        finally:
            self._cleanup_resources()

    def _handle_connect_operation(self) -> None:
        if len(self.args) < 6:
            raise ValueError("Operacao de conexao requer db_type, host, port, username, password e database")

        db_type, host, port, username, password, database = self.args[:6]

        self.progress.emit(30)
        connection_params = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database,
        }

        self.progress.emit(50)

        try:
            # This is a thread-local connection test. The resulting connection
            # is closed before the worker finishes and is not shared with the UI.
            test_manager = DatabaseManager()
            success = test_manager.connect(db_type, **connection_params)
            test_manager.disconnect_all()

            self.progress.emit(100)
            if success:
                self.finished.emit(True, f"Conectado com sucesso ao banco: {db_type}", None)
            else:
                self.finished.emit(False, f"Falha ao conectar ao banco: {db_type}", None)
        except ConnectionError as exc:
            self.progress.emit(100)
            self.finished.emit(False, str(exc), None)

    def _handle_execute_query_operation(self) -> None:
        if len(self.args) < 1:
            raise ValueError("Operacao de execucao de query requer uma query")

        query = self.args[0]
        db_type = self.kwargs.get("db_type")

        self.progress.emit(20)

        try:
            manager = self._create_operation_manager()
            self.progress.emit(40)

            result = manager.execute_query(query, db_type)
            self.progress.emit(100)
            self.finished.emit(result.success, result.message, result)
        except (ConnectionError, QueryExecutionError) as exc:
            self.progress.emit(100)
            self.finished.emit(False, str(exc), None)

    def _handle_custom_operation(self) -> None:
        operation_instance = self.kwargs.get("operation_instance")
        parameters = self.kwargs.get("parameters", {})

        if not operation_instance:
            raise ValueError("Operacao customizada requer operation_instance")

        self.progress.emit(20)

        try:
            manager = self._create_operation_manager()
            self.progress.emit(40)

            result = operation_instance.execute(manager, **parameters)
            self.progress.emit(80)

            from ..database.drivers.base import QueryResult

            query_result = QueryResult(
                success=result.success,
                message=result.message,
                columns=result.columns,
                data=result.data,
                rows_affected=result.rows_affected,
            )

            self.progress.emit(100)
            self.finished.emit(result.success, result.message, query_result)
        except Exception as exc:
            self.progress.emit(100)
            logger.exception("Erro na operacao customizada %s", self.operation_name)
            self.finished.emit(False, f"Erro na operacao: {exc}", None)

    def _handle_disconnect_operation(self) -> None:
        self.progress.emit(100)
        self.finished.emit(True, "Desconectado do banco de dados.", None)

    def _create_operation_manager(self) -> DatabaseManager:
        """Create a thread-local manager when connection_config is provided."""
        connection_config = self.kwargs.get("connection_config")
        if not connection_config:
            if not self.db_manager.is_connected():
                raise ConnectionError("Nao conectado ao banco de dados")
            return self.db_manager

        self._local_db_manager = DatabaseManager()
        db_type = connection_config["db_type"]
        params = {
            "host": connection_config["host"],
            "port": connection_config["port"],
            "username": connection_config["username"],
            "password": connection_config["password"],
            "database": connection_config["database"],
        }
        self._local_db_manager.connect(db_type, **params)
        return self._local_db_manager

    def _cleanup_resources(self) -> None:
        try:
            if self._local_db_manager:
                self._local_db_manager.disconnect_all()
                self._local_db_manager = None
            self._cleanup_required = False
        except Exception as exc:
            logger.warning("Erro de limpeza no DatabaseWorker: %s", exc)

    def stop(self) -> None:
        if self.isRunning():
            self.requestInterruption()
            self._cleanup_required = True

    def get_operation_info(self) -> dict:
        return {
            "operation": self.operation,
            "operation_name": self.operation_name,
            "args_count": len(self.args),
            "kwargs_count": len(self.kwargs),
            "is_running": self.isRunning(),
            "cleanup_required": self._cleanup_required,
        }


class DatabaseWorkerFactory:
    """Factory for common worker configurations."""

    @staticmethod
    def create_connection_worker(
        db_manager: DatabaseManager,
        db_type: str,
        host: str,
        port: str,
        username: str,
        password: str,
        database: str,
    ) -> DatabaseWorker:
        return DatabaseWorker(
            db_manager,
            "connect",
            f"Connect to {db_type}",
            db_type,
            host,
            port,
            username,
            password,
            database,
        )

    @staticmethod
    def create_query_worker(
        db_manager: DatabaseManager,
        query: str,
        operation_name: str = "Execute Query",
        db_type: Optional[str] = None,
        connection_config: Optional[dict] = None,
    ) -> DatabaseWorker:
        kwargs = {"db_type": db_type} if db_type else {}
        if connection_config:
            kwargs["connection_config"] = connection_config
        return DatabaseWorker(db_manager, "execute_query", operation_name, query, **kwargs)

    @staticmethod
    def create_disconnect_worker(db_manager: DatabaseManager, db_type: Optional[str] = None) -> DatabaseWorker:
        args = (db_type,) if db_type else ()
        operation_name = f"Disconnect from {db_type}" if db_type else "Disconnect"
        return DatabaseWorker(db_manager, "disconnect", operation_name, *args)

    @staticmethod
    def create_custom_operation_worker(
        db_manager: DatabaseManager,
        operation_instance: Any,
        operation_name: str,
        parameters: Optional[dict] = None,
        connection_config: Optional[dict] = None,
    ) -> DatabaseWorker:
        return DatabaseWorker(
            db_manager,
            "custom_operation",
            operation_name,
            operation_instance=operation_instance,
            parameters=parameters or {},
            connection_config=connection_config,
        )
