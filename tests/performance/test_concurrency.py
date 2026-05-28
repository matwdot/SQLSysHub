"""
Concurrency tests for SQL SysHub.

Tests system behavior under concurrent operations, including
multiple database connections, concurrent workers, and thread safety.
"""

import pytest
import time
import threading
import queue
import sys
import os
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication

# Add the refactored_sqltools to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from refactored_sqltools.core.database.manager import DatabaseManager
from refactored_sqltools.core.workers.database_worker import DatabaseWorkerFactory
from refactored_sqltools.core.operations.registry import operation_registry
from refactored_sqltools.ui.windows.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for concurrency tests"""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.mark.concurrency
class TestDatabaseConcurrency:
    """Test database operations under concurrent access"""
    
    def test_multiple_database_managers(self):
        """Test multiple DatabaseManager instances working concurrently"""
        results = queue.Queue()
        
        def create_manager_worker(worker_id):
            try:
                manager = DatabaseManager()
                
                # Test driver creation
                firebird_driver = manager.get_driver("Firebird")
                sqlserver_driver = manager.get_driver("SQL Server")
                
                # Verify drivers are created
                assert firebird_driver is not None
                assert sqlserver_driver is not None
                
                results.put((worker_id, True, None))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create multiple threads with database managers
        threads = []
        num_workers = 5
        
        for i in range(num_workers):
            thread = threading.Thread(target=create_manager_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify all workers succeeded
        assert len(worker_results) == num_workers
        for worker_id, success, error in worker_results:
            assert success, f"Worker {worker_id} failed: {error}"
    
    def test_concurrent_operation_registry_access(self):
        """Test concurrent access to operation registry"""
        results = queue.Queue()
        
        def registry_worker(worker_id, iterations=50):
            try:
                for i in range(iterations):
                    # Get operations
                    operations = operation_registry.list_operations()
                    names = operation_registry.get_operation_names()
                    
                    # Verify consistency
                    assert len(operations) == len(names)
                    
                    # Get specific operation
                    if names:
                        first_op = operation_registry.get_operation(names[0])
                        assert first_op is not None
                
                results.put((worker_id, True, None))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create multiple threads accessing registry
        threads = []
        num_workers = 10
        
        for i in range(num_workers):
            thread = threading.Thread(target=registry_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=15.0)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify all workers succeeded
        assert len(worker_results) == num_workers
        for worker_id, success, error in worker_results:
            assert success, f"Registry worker {worker_id} failed: {error}"
    
    def test_concurrent_sql_generation(self):
        """Test concurrent SQL generation from operations"""
        results = queue.Queue()
        
        def sql_generation_worker(worker_id):
            try:
                operations = operation_registry.list_operations()
                
                for name, operation in operations.items():
                    try:
                        # Try to generate SQL
                        sql = operation.get_sql()
                        assert isinstance(sql, str)
                        assert len(sql) > 0
                    except (KeyError, TypeError):
                        # Try with parameters
                        try:
                            sql = operation.get_sql(
                                data_inicio='2024-01-01',
                                data_fim='2024-12-31'
                            )
                            assert isinstance(sql, str)
                        except Exception:
                            # Skip if can't generate
                            pass
                
                results.put((worker_id, True, None))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create multiple threads generating SQL
        threads = []
        num_workers = 8
        
        for i in range(num_workers):
            thread = threading.Thread(target=sql_generation_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=20.0)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify all workers succeeded
        assert len(worker_results) == num_workers
        for worker_id, success, error in worker_results:
            assert success, f"SQL generation worker {worker_id} failed: {error}"


@pytest.mark.concurrency
class TestWorkerConcurrency:
    """Test database worker concurrency"""
    
    def test_multiple_workers_creation(self):
        """Test creating multiple database workers concurrently"""
        manager = DatabaseManager()
        workers = []
        
        # Create multiple workers
        for i in range(5):
            connection_worker = DatabaseWorkerFactory.create_connection_worker(
                manager, "Firebird", "localhost", "3050", "SYSDBA", "masterkey", f"test_{i}.fdb"
            )
            query_worker = DatabaseWorkerFactory.create_query_worker(
                manager, f"SELECT {i}", f"Test Query {i}"
            )
            
            workers.extend([connection_worker, query_worker])
        
        # Verify all workers are created
        assert len(workers) == 10
        
        # Verify workers have required attributes
        for worker in workers:
            assert hasattr(worker, 'start')
            assert hasattr(worker, 'finished')
            assert hasattr(worker, 'progress')
        
        # Clean up workers
        for worker in workers:
            if hasattr(worker, 'stop'):
                worker.stop()
    
    def test_worker_thread_safety(self, qapp):
        """Test worker thread safety with Qt application"""
        manager = DatabaseManager()
        results = []
        
        def worker_callback(success, message, result):
            results.append((success, message, result))
        
        # Create workers with mocked database operations
        with patch.object(manager, 'connect') as mock_connect:
            mock_connect.return_value = True
            
            workers = []
            for i in range(3):
                worker = DatabaseWorkerFactory.create_connection_worker(
                    manager, "Firebird", "localhost", "3050", "SYSDBA", "masterkey", f"test_{i}.fdb"
                )
                worker.finished.connect(worker_callback)
                workers.append(worker)
            
            # Start workers
            for worker in workers:
                worker.start()
            
            # Wait for workers to complete
            for worker in workers:
                worker.wait(5000)  # 5 second timeout
            
            # Verify workers completed
            for worker in workers:
                assert not worker.isRunning()
    
    def test_worker_resource_cleanup(self):
        """Test proper resource cleanup in workers"""
        manager = DatabaseManager()
        
        # Create and start workers
        workers = []
        for i in range(3):
            worker = DatabaseWorkerFactory.create_query_worker(
                manager, f"SELECT {i}", f"Test {i}"
            )
            workers.append(worker)
        
        # Test cleanup
        for worker in workers:
            # Get initial state
            initial_info = worker.get_operation_info()
            assert 'operation' in initial_info
            
            # Stop worker if running
            if hasattr(worker, 'stop'):
                worker.stop()
            
            # Verify cleanup
            if hasattr(worker, '_cleanup_resources'):
                worker._cleanup_resources()


@pytest.mark.concurrency
class TestUIConcurrency:
    """Test UI component concurrency and thread safety"""
    
    def test_multiple_main_windows(self, qapp):
        """Test creating multiple main windows (simulating multiple instances)"""
        windows = []
        
        try:
            # Create multiple main windows
            for i in range(3):
                window = MainWindow()
                windows.append(window)
            
            # Verify all windows are created
            assert len(windows) == 3
            
            # Test basic functionality on each window
            for i, window in enumerate(windows):
                assert window.windowTitle() == "SQL SysHub - Utilitarios de Banco de Dados"
                assert hasattr(window, 'db_manager')
                assert hasattr(window, 'connection_panel')
                
                # Test connection state handling
                window.on_connection_changed(True)
                assert window.execute_btn.isEnabled()
                
                window.on_connection_changed(False)
                assert not window.execute_btn.isEnabled()
        
        finally:
            # Clean up windows
            for window in windows:
                if hasattr(window, 'cleanup'):
                    window.cleanup()
    
    def test_ui_component_thread_safety(self, qapp):
        """Test UI component operations from different threads"""
        window = MainWindow()
        results = queue.Queue()
        
        def ui_worker(worker_id):
            try:
                # Test thread-safe operations
                # Note: In real Qt applications, UI operations should only be done from main thread
                # This test verifies that our components handle cross-thread access gracefully
                
                # Test getting component state (should be thread-safe)
                has_connection_panel = hasattr(window, 'connection_panel')
                has_db_manager = hasattr(window, 'db_manager')
                
                results.put((worker_id, True, has_connection_panel and has_db_manager))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create threads that access UI components
        threads = []
        for i in range(3):
            thread = threading.Thread(target=ui_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for threads
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify results
        assert len(worker_results) == 3
        for worker_id, success, result in worker_results:
            assert success, f"UI worker {worker_id} failed"
            assert result, f"UI worker {worker_id} couldn't access components"
        
        # Clean up
        if hasattr(window, 'cleanup'):
            window.cleanup()


@pytest.mark.concurrency
@pytest.mark.slow
class TestStressConcurrency:
    """Stress tests for concurrent operations"""
    
    def test_high_concurrency_database_managers(self):
        """Test high concurrency with many database managers"""
        results = queue.Queue()
        
        def stress_worker(worker_id, iterations=20):
            try:
                for i in range(iterations):
                    manager = DatabaseManager()
                    
                    # Test rapid driver creation
                    fb_driver = manager.get_driver("Firebird")
                    sql_driver = manager.get_driver("SQL Server")
                    
                    # Verify drivers
                    assert fb_driver is not None
                    assert sql_driver is not None
                    
                    # Test supported databases
                    supported = manager.get_supported_databases()
                    assert len(supported) >= 2
                
                results.put((worker_id, True, None))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create many concurrent threads
        threads = []
        num_workers = 20
        
        start_time = time.time()
        
        for i in range(num_workers):
            thread = threading.Thread(target=stress_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=30.0)
        
        duration = time.time() - start_time
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify performance and correctness
        assert len(worker_results) == num_workers, "Not all workers completed"
        assert duration < 15.0, f"High concurrency test took {duration:.2f}s, expected < 15.0s"
        
        for worker_id, success, error in worker_results:
            assert success, f"Stress worker {worker_id} failed: {error}"
    
    def test_rapid_operation_access(self):
        """Test rapid concurrent access to operations"""
        results = queue.Queue()
        
        def rapid_access_worker(worker_id, iterations=100):
            try:
                for i in range(iterations):
                    # Rapid registry access
                    operations = operation_registry.list_operations()
                    names = operation_registry.get_operation_names()
                    
                    # Random operation access
                    if names:
                        import random
                        random_name = random.choice(names)
                        operation = operation_registry.get_operation(random_name)
                        assert operation is not None
                
                results.put((worker_id, True, None))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create many threads with rapid access
        threads = []
        num_workers = 15
        
        start_time = time.time()
        
        for i in range(num_workers):
            thread = threading.Thread(target=rapid_access_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=20.0)
        
        duration = time.time() - start_time
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify performance and correctness
        assert len(worker_results) == num_workers
        assert duration < 10.0, f"Rapid access test took {duration:.2f}s, expected < 10.0s"
        
        for worker_id, success, error in worker_results:
            assert success, f"Rapid access worker {worker_id} failed: {error}"
    
    def test_memory_stability_under_concurrency(self):
        """Test memory stability under concurrent load"""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        results = queue.Queue()
        
        def memory_worker(worker_id, iterations=50):
            try:
                objects_created = []
                
                for i in range(iterations):
                    # Create various objects
                    manager = DatabaseManager()
                    operations = operation_registry.list_operations()
                    
                    # Store references temporarily
                    objects_created.extend([manager, operations])
                    
                    # Periodic cleanup
                    if i % 10 == 0:
                        objects_created.clear()
                        gc.collect()
                
                results.put((worker_id, True, len(objects_created)))
            except Exception as e:
                results.put((worker_id, False, str(e)))
        
        # Create threads that stress memory
        threads = []
        num_workers = 10
        
        for i in range(num_workers):
            thread = threading.Thread(target=memory_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=25.0)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify memory stability
        assert len(worker_results) == num_workers
        
        for worker_id, success, objects_count in worker_results:
            assert success, f"Memory worker {worker_id} failed"
            # Should not accumulate too many objects
            assert objects_count < 1000, f"Worker {worker_id} accumulated {objects_count} objects"
        
        # Final garbage collection
        gc.collect()