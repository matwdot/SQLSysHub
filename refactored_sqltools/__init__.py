"""
Refactored SQLTools system.

A modular refactoring of the original SQLTools.py monolithic application.
"""

from .core import DatabaseManager, DatabaseDriver, QueryResult
from .utils import SQLSysHubException, ConnectionError, QueryExecutionError, ValidationError

__version__ = "1.0.0"

__all__ = [
    'DatabaseManager',
    'DatabaseDriver',
    'QueryResult',
    'SQLSysHubException',
    'ConnectionError',
    'QueryExecutionError', 
    'ValidationError'
]