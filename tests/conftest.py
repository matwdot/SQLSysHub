"""
Pytest configuration and shared fixtures.
"""

import pytest
from hypothesis import settings, Verbosity


# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.load_profile("default")


@pytest.fixture
def sample_connection_params():
    """Sample connection parameters for testing."""
    return {
        'firebird': {
            'host': 'localhost',
            'port': '3050',
            'database': '/path/to/test.fdb',
            'username': 'SYSDBA',
            'password': 'masterkey'
        },
        'sqlserver': {
            'host': 'localhost',
            'port': '1433',
            'database': 'TestDB',
            'username': 'sa',
            'password': 'TestPassword123'
        }
    }


@pytest.fixture
def sample_query_result():
    """Sample query result for testing."""
    return {
        'success': True,
        'message': 'Query executed successfully',
        'columns': ['id', 'name', 'email'],
        'data': [
            (1, 'John Doe', 'john@example.com'),
            (2, 'Jane Smith', 'jane@example.com')
        ],
        'rows_affected': 2
    }