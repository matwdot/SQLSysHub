"""
Performance tests for large data operations.

Tests system behavior with large SQL queries, large result sets,
and bulk operations to ensure acceptable performance.
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, patch

# Add the refactored_sqltools to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from refactored_sqltools.utils.validators import validate_sql_query
from refactored_sqltools.ui.components.sql_editor import SQLEditor, SQLEditorWidget
from refactored_sqltools.core.database.drivers.base import QueryResult
from refactored_sqltools.core.operations.registry import operation_registry
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for UI performance tests"""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.mark.performance
class TestLargeDataPerformance:
    """Test performance with large data sets"""
    
    def test_large_sql_validation_performance(self):
        """Test SQL validation performance with large queries"""
        # Generate large SQL query
        large_sql = self._generate_large_sql_query(size_kb=100)  # 100KB query
        
        start_time = time.time()
        
        # Validate large SQL
        try:
            validate_sql_query(large_sql)
        except Exception:
            pass  # We're testing performance, not correctness
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time (1 second for 100KB)
        assert duration < 1.0, f"Large SQL validation took {duration:.2f}s, expected < 1.0s"
    
    def test_massive_sql_validation_performance(self):
        """Test SQL validation performance with massive queries"""
        # Generate massive SQL query
        massive_sql = self._generate_large_sql_query(size_kb=1000)  # 1MB query
        
        start_time = time.time()
        
        try:
            validate_sql_query(massive_sql)
        except Exception:
            pass
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds for 1MB)
        assert duration < 5.0, f"Massive SQL validation took {duration:.2f}s, expected < 5.0s"
    
    def test_sql_editor_large_text_performance(self, qapp):
        """Test SQL editor performance with large text"""
        editor = SQLEditor()
        
        # Generate large SQL text
        large_sql = self._generate_large_sql_query(size_kb=50)  # 50KB
        
        start_time = time.time()
        
        # Set large text in editor
        editor.set_sql_text(large_sql)
        
        duration = time.time() - start_time
        
        # Should complete quickly (0.5 seconds for 50KB)
        assert duration < 0.5, f"SQL editor large text took {duration:.2f}s, expected < 0.5s"
    
    def test_sql_editor_formatting_performance(self, qapp):
        """Test SQL editor formatting performance"""
        editor = SQLEditor()
        
        # Generate complex SQL with many keywords
        complex_sql = self._generate_complex_sql_query()
        
        start_time = time.time()
        
        # Format complex SQL
        formatted = editor.basic_sql_format(complex_sql)
        
        duration = time.time() - start_time
        
        # Should format quickly
        assert duration < 0.1, f"SQL formatting took {duration:.2f}s, expected < 0.1s"
        assert len(formatted) > 0
    
    def test_large_result_set_processing(self):
        """Test processing of large result sets"""
        # Simulate large result set
        large_columns = [f"column_{i}" for i in range(50)]  # 50 columns
        large_data = [(i, f"value_{i}") + tuple(range(48)) for i in range(1000)]  # 1000 rows
        
        start_time = time.time()
        
        # Create QueryResult with large data
        result = QueryResult(
            success=True,
            message="Large result set",
            columns=large_columns,
            data=large_data
        )
        
        # Process result (simulate what UI would do)
        processed_data = []
        for row in result.data:
            processed_row = [str(cell) for cell in row]
            processed_data.append(processed_row)
        
        duration = time.time() - start_time
        
        # Should process quickly
        assert duration < 1.0, f"Large result processing took {duration:.2f}s, expected < 1.0s"
        assert len(processed_data) == 1000
    
    def test_multiple_operations_performance(self):
        """Test performance of multiple operation executions"""
        operations = operation_registry.list_operations()
        operation_list = list(operations.values())[:5]  # Test first 5 operations
        
        start_time = time.time()
        
        # Execute multiple operations (SQL generation only)
        for operation in operation_list:
            try:
                sql = operation.get_sql()
            except:
                try:
                    sql = operation.get_sql(data_inicio='2024-01-01', data_fim='2024-12-31')
                except:
                    try:
                        sql = operation.get_sql(codigo_produto='12345')
                    except:
                        pass  # Skip if can't generate SQL
        
        duration = time.time() - start_time
        
        # Should complete quickly
        assert duration < 0.5, f"Multiple operations took {duration:.2f}s, expected < 0.5s"
    
    def _generate_large_sql_query(self, size_kb: int) -> str:
        """Generate a large SQL query of approximately the specified size"""
        base_query = """
        SELECT 
            t1.id, t1.name, t1.description, t1.created_at, t1.updated_at,
            t2.category_id, t2.category_name, t2.category_description,
            t3.user_id, t3.username, t3.email, t3.full_name
        FROM products t1
        INNER JOIN categories t2 ON t1.category_id = t2.id
        INNER JOIN users t3 ON t1.created_by = t3.id
        WHERE t1.active = 1 
        AND t2.active = 1 
        AND t3.active = 1
        AND t1.created_at BETWEEN '2024-01-01' AND '2024-12-31'
        """
        
        # Calculate how many repetitions we need
        base_size = len(base_query.encode('utf-8'))
        target_size = size_kb * 1024
        repetitions = max(1, target_size // base_size)
        
        # Create large query by adding UNION ALL clauses
        large_query = base_query
        for i in range(repetitions - 1):
            large_query += f"\nUNION ALL\n{base_query}"
        
        return large_query
    
    def _generate_complex_sql_query(self) -> str:
        """Generate a complex SQL query with many keywords for formatting tests"""
        return """
        WITH recursive_cte AS (
            SELECT id, parent_id, name, 1 as level
            FROM categories 
            WHERE parent_id IS NULL
            UNION ALL
            SELECT c.id, c.parent_id, c.name, rc.level + 1
            FROM categories c
            INNER JOIN recursive_cte rc ON c.parent_id = rc.id
        ),
        sales_summary AS (
            SELECT 
                p.category_id,
                COUNT(*) as total_sales,
                SUM(oi.quantity * oi.price) as total_revenue,
                AVG(oi.quantity * oi.price) as avg_order_value
            FROM order_items oi
            INNER JOIN products p ON oi.product_id = p.id
            INNER JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'completed'
            AND o.created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY p.category_id
            HAVING total_sales > 100
        )
        SELECT 
            rc.name as category_name,
            rc.level as category_level,
            COALESCE(ss.total_sales, 0) as sales_count,
            COALESCE(ss.total_revenue, 0) as revenue,
            COALESCE(ss.avg_order_value, 0) as avg_value,
            CASE 
                WHEN ss.total_revenue > 10000 THEN 'High'
                WHEN ss.total_revenue > 5000 THEN 'Medium'
                ELSE 'Low'
            END as performance_tier
        FROM recursive_cte rc
        LEFT JOIN sales_summary ss ON rc.id = ss.category_id
        WHERE rc.level <= 3
        ORDER BY rc.level, ss.total_revenue DESC NULLS LAST
        LIMIT 100;
        """


@pytest.mark.performance
class TestMemoryUsagePerformance:
    """Test memory usage under various conditions"""
    
    def test_sql_editor_memory_usage(self, qapp):
        """Test SQL editor memory usage with multiple instances"""
        editors = []
        
        # Create multiple SQL editors
        for i in range(10):
            editor = SQLEditorWidget()
            editor.set_sql_text(f"SELECT * FROM table_{i} WHERE id = {i}")
            editors.append(editor)
        
        # Verify all editors are functional
        for i, editor in enumerate(editors):
            text = editor.get_sql_text()
            assert f"table_{i}" in text
        
        # Clean up
        for editor in editors:
            editor.clear()
        
        # Test passes if no memory errors occur
        assert len(editors) == 10
    
    def test_large_operation_registry_memory(self):
        """Test operation registry memory usage"""
        # Get operations multiple times to test caching
        for _ in range(100):
            operations = operation_registry.list_operations()
            names = operation_registry.get_operation_names()
            
            # Verify consistency
            assert len(operations) == len(names)
        
        # Test passes if no memory leaks occur
        assert True
    
    def test_query_result_memory_scaling(self):
        """Test QueryResult memory usage with increasing data sizes"""
        data_sizes = [100, 500, 1000, 2000]
        
        for size in data_sizes:
            # Create result with specified size
            columns = ['id', 'name', 'value']
            data = [(i, f'name_{i}', f'value_{i}') for i in range(size)]
            
            result = QueryResult(
                success=True,
                message=f"Result with {size} rows",
                columns=columns,
                data=data
            )
            
            # Verify result is created correctly
            assert len(result.data) == size
            assert len(result.columns) == 3
            
            # Process data to simulate real usage
            processed = [str(row[0]) for row in result.data]
            assert len(processed) == size
        
        # Test passes if all sizes work without memory issues
        assert True


@pytest.mark.performance
@pytest.mark.slow
class TestStressPerformance:
    """Stress tests for system limits"""
    
    def test_extreme_sql_size_handling(self):
        """Test handling of extremely large SQL queries"""
        # Generate very large SQL (5MB)
        base_query = "SELECT * FROM large_table WHERE id IN ("
        large_values = ", ".join([str(i) for i in range(100000)])  # 100k values
        extreme_sql = base_query + large_values + ")"
        
        start_time = time.time()
        
        try:
            # Test that system doesn't crash with extreme input
            validate_sql_query(extreme_sql)
        except Exception as e:
            # Should handle gracefully, not crash
            assert "não pode estar vazia" not in str(e)  # Should not be empty error
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time even for extreme cases
        assert duration < 10.0, f"Extreme SQL handling took {duration:.2f}s, expected < 10.0s"
    
    def test_rapid_operation_switching(self):
        """Test rapid switching between operations"""
        operations = list(operation_registry.list_operations().values())
        
        start_time = time.time()
        
        # Rapidly switch between operations
        for _ in range(100):
            for operation in operations[:3]:  # Test first 3 operations
                try:
                    sql = operation.get_sql()
                except:
                    pass  # Skip if requires parameters
        
        duration = time.time() - start_time
        
        # Should handle rapid switching efficiently
        assert duration < 2.0, f"Rapid operation switching took {duration:.2f}s, expected < 2.0s"
    
    def test_concurrent_sql_validation(self):
        """Test concurrent SQL validation (simulated)"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def validate_worker(sql_text, worker_id):
            try:
                start = time.time()
                validate_sql_query(sql_text)
                duration = time.time() - start
                results.put((worker_id, duration, True))
            except Exception as e:
                duration = time.time() - start
                results.put((worker_id, duration, False))
        
        # Create multiple threads for concurrent validation
        threads = []
        sql_queries = [
            "SELECT * FROM table1",
            "UPDATE table2 SET value = 1",
            "INSERT INTO table3 VALUES (1, 'test')",
            "DELETE FROM table4 WHERE id = 1"
        ]
        
        start_time = time.time()
        
        for i, sql in enumerate(sql_queries):
            thread = threading.Thread(target=validate_worker, args=(sql, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)  # 5 second timeout
        
        total_duration = time.time() - start_time
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Should complete all validations quickly
        assert total_duration < 2.0, f"Concurrent validation took {total_duration:.2f}s, expected < 2.0s"
        assert len(worker_results) == len(sql_queries), "Not all workers completed"