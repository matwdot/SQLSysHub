"""
Custom exceptions for the SQL SysHub refactored system.

This module defines the exception hierarchy used throughout the application
for better error handling and debugging.
"""


class SQLSysHubException(Exception):
    """Base exception for all SQL SysHub-related errors."""
    pass


class ConnectionError(SQLSysHubException):
    """Raised when database connection operations fail."""
    pass


class QueryExecutionError(SQLSysHubException):
    """Raised when SQL query execution fails."""
    pass


class ValidationError(SQLSysHubException):
    """Raised when parameter validation fails."""
    pass


class DriverImportError(SQLSysHubException):
    """Raised when database driver import fails."""
    pass