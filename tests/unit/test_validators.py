"""
Unit tests for the validators module.

Tests validation functions for database connections, date ranges,
and file paths.
"""

import pytest
import tempfile
import os
from refactored_sqltools.utils.validators import (
    validate_connection_params,
    validate_firebird_database_path,
    validate_date_range,
    validate_sql_query
)
from refactored_sqltools.utils.exceptions import ValidationError


class TestConnectionValidation:
    """Test database connection parameter validation."""
    
    def test_firebird_connection_validation_success(self):
        """Test successful Firebird connection validation with existing file."""
        # Create a temporary file to simulate database
        with tempfile.NamedTemporaryFile(suffix='.fdb', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = validate_connection_params(
                'firebird',
                database=temp_path,
                host='localhost',
                username='SYSDBA',
                password='masterkey'
            )
            assert result is True
        finally:
            os.unlink(temp_path)
    
    def test_firebird_connection_validation_missing_file(self):
        """Test Firebird connection validation with missing file."""
        with pytest.raises(ValidationError, match="Arquivo de banco não encontrado"):
            validate_connection_params(
                'firebird',
                database='/nonexistent/path/test.fdb',
                host='localhost'
            )
    
    def test_firebird_connection_validation_missing_database(self):
        """Test Firebird connection validation with missing database parameter."""
        with pytest.raises(ValidationError, match="Parâmetros obrigatórios ausentes"):
            validate_connection_params('firebird', host='localhost')
    
    def test_sqlserver_connection_validation_success(self):
        """Test successful SQL Server connection validation."""
        result = validate_connection_params(
            'sqlserver',
            database='testdb',
            host='localhost',
            username='sa',
            password='password'
        )
        assert result is True
    
    def test_sqlserver_connection_validation_missing_database(self):
        """Test SQL Server connection validation with missing database."""
        with pytest.raises(ValidationError, match="Parâmetros obrigatórios ausentes"):
            validate_connection_params('sqlserver', host='localhost')
    
    def test_unsupported_database_type(self):
        """Test validation with unsupported database type."""
        with pytest.raises(ValidationError, match="Tipo de banco não suportado"):
            validate_connection_params('mysql', database='test')


class TestFirebirdPathValidation:
    """Test Firebird database path validation."""
    
    def test_valid_existing_file(self):
        """Test validation with existing file."""
        with tempfile.NamedTemporaryFile(suffix='.fdb', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = validate_firebird_database_path(temp_path, 'localhost')
            assert result is True
        finally:
            os.unlink(temp_path)
    
    def test_empty_path(self):
        """Test validation with empty path."""
        with pytest.raises(ValidationError, match="Caminho do banco não pode estar vazio"):
            validate_firebird_database_path('', 'localhost')
    
    def test_nonexistent_file_local(self):
        """Test validation with nonexistent file for local connection."""
        with pytest.raises(ValidationError, match="Arquivo de banco não encontrado"):
            validate_firebird_database_path('/nonexistent/test.fdb', 'localhost')
    
    def test_remote_path_validation(self):
        """Test validation for remote database path."""
        # Remote paths don't need to exist locally
        result = validate_firebird_database_path('/remote/path/test.fdb', 'remote-server')
        assert result is True
    
    def test_invalid_characters_remote(self):
        """Test validation with invalid characters in remote path."""
        with pytest.raises(ValidationError, match="contém caracteres inválidos"):
            validate_firebird_database_path('/path/with<invalid>chars.fdb', 'remote-server')


class TestDateRangeValidation:
    """Test date range validation."""
    
    def test_valid_date_range(self):
        """Test validation with valid date range."""
        result = validate_date_range('2024-01-01', '2024-12-31')
        assert result is True
    
    def test_same_dates(self):
        """Test validation with same start and end dates."""
        result = validate_date_range('2024-06-15', '2024-06-15')
        assert result is True
    
    def test_invalid_date_order(self):
        """Test validation with start date after end date."""
        with pytest.raises(ValidationError, match="Data de início deve ser anterior"):
            validate_date_range('2024-12-31', '2024-01-01')
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format."""
        with pytest.raises(ValidationError, match="Formato de data inválido"):
            validate_date_range('2024/01/01', '2024/12/31')
    
    def test_empty_dates(self):
        """Test validation with empty dates."""
        with pytest.raises(ValidationError, match="Datas de início e fim são obrigatórias"):
            validate_date_range('', '2024-12-31')
    
    def test_dates_too_old(self):
        """Test validation with dates too far in the past."""
        with pytest.raises(ValidationError, match="não podem ser anteriores"):
            validate_date_range('1999-01-01', '1999-12-31')
    
    def test_dates_too_future(self):
        """Test validation with dates too far in the future."""
        with pytest.raises(ValidationError, match="não podem ser posteriores"):
            validate_date_range('2030-01-01', '2030-12-31')


class TestSQLQueryValidation:
    """Test SQL query validation."""
    
    def test_valid_select_query(self):
        """Test validation with valid SELECT query."""
        result = validate_sql_query('SELECT * FROM users WHERE id = 1')
        assert result is True
    
    def test_valid_update_query(self):
        """Test validation with valid UPDATE query."""
        result = validate_sql_query("UPDATE users SET name = 'John' WHERE id = 1")
        assert result is True
    
    def test_empty_query(self):
        """Test validation with empty query."""
        with pytest.raises(ValidationError, match="Query SQL não pode estar vazia"):
            validate_sql_query('')
    
    def test_dangerous_drop_query(self):
        """Test validation rejects dangerous DROP query."""
        with pytest.raises(ValidationError, match="padrão potencialmente perigoso"):
            validate_sql_query('SELECT * FROM users; DROP TABLE users;')
    
    def test_dangerous_delete_query(self):
        """Test validation rejects dangerous DELETE query."""
        with pytest.raises(ValidationError, match="padrão potencialmente perigoso"):
            validate_sql_query('SELECT * FROM users; DELETE FROM users;')
    
    def test_sql_comment_injection(self):
        """Test validation rejects SQL comment injection."""
        with pytest.raises(ValidationError, match="padrão potencialmente perigoso"):
            validate_sql_query('SELECT * FROM users WHERE id = 1 -- AND password = "secret"')