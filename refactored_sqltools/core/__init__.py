"""
Core package.

This package contains the core business logic of the refactored SQLTools system.
"""

from .database import DatabaseManager, DatabaseDriver, QueryResult

__all__ = [
    'DatabaseManager',
    'DatabaseDriver', 
    'QueryResult'
]