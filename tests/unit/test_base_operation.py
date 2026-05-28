"""
Unit tests for BaseOperation class.
"""

import pytest
from refactored_sqltools.core.operations.base import BaseOperation, OperationResult
from refactored_sqltools.utils.exceptions import ValidationError


class MockOperation(BaseOperation):
    """Mock implementation of BaseOperation for testing."""
    
    def __init__(self, name="test_op", description="Test operation"):
        super().__init__(name, description)
        self.validation_should_pass = True
        self.sql_to_return = "SELECT 1"
    
    def get_sql(self, **params) -> str:
        if 'invalid' in params:
            raise ValueError("Invalid parameter")
        return self.sql_to_return
    
    def validate_params(self, **params) -> bool:
        if not self.validation_should_pass:
            raise ValidationError("Validation failed")
        return True


class MockDatabaseManager:
    """Mock database manager for testing."""
    
    def __init__(self):
        self.query_result = {
            'rows_affected': 1
        }
    
    def execute_query(self, sql: str, params=None) -> dict:
        return self.query_result


class TestBaseOperation:
    """Test cases for BaseOperation class."""
    
    def test_successful_operation_execution(self):
        """Test successful operation execution."""
        op = MockOperation()
        db_manager = MockDatabaseManager()
        
        result = op.execute(db_manager, param1="value1")
        
        assert isinstance(result, OperationResult)
        assert result.success is True
        assert "Operação executada com sucesso" in result.message
        assert result.rows_affected == 1
    
    def test_operation_execution_with_validation_failure(self):
        """Test operation execution when validation fails."""
        op = MockOperation()
        op.validation_should_pass = False
        db_manager = MockDatabaseManager()
        
        result = op.execute(db_manager)
        
        assert result.success is False
        assert "Erro de validação" in result.message
    
    def test_operation_execution_with_sql_generation_error(self):
        """Test operation execution when SQL generation fails."""
        op = MockOperation()
        db_manager = MockDatabaseManager()
        
        result = op.execute(db_manager, invalid="param")
        
        assert result.success is False
        assert "Falha na operação" in result.message
    
    def test_operation_execution_with_database_error(self):
        """Test operation execution when database query fails."""
        op = MockOperation()
        db_manager = MockDatabaseManager()
        
        # Simulate database error by making execute_query raise an exception
        def failing_execute_query(sql):
            raise Exception("Database connection failed")
        
        db_manager.execute_query = failing_execute_query
        
        result = op.execute(db_manager)
        
        assert result.success is False
        assert "Falha na operação" in result.message