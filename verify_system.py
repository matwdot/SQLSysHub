#!/usr/bin/env python3
"""
Simple system verification script to check if the refactored SQL SysHub system is working.
"""

def verify_imports():
    """Verify all core modules can be imported."""
    try:
        # Core imports
        from refactored_sqltools.core.database.manager import DatabaseManager
        from refactored_sqltools.core.database.drivers.firebird import FirebirdDriver
        from refactored_sqltools.core.database.drivers.sqlserver import SqlServerDriver
        from refactored_sqltools.core.operations.predefined import operation_registry
        from refactored_sqltools.core.workers.database_worker import DatabaseWorker
        
        # UI imports
        from refactored_sqltools.ui.windows.main_window import MainWindow
        from refactored_sqltools.ui.components.connection_panel import ConnectionPanel
        from refactored_sqltools.ui.components.operation_selector import OperationSelector
        from refactored_sqltools.ui.components.results_display import ResultsDisplay
        from refactored_sqltools.ui.components.progress_indicator import ProgressIndicator
        
        # Utils imports
        from refactored_sqltools.utils.exceptions import SQLSysHubException
        from refactored_sqltools.utils.validators import validate_connection_params
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def verify_operations():
    """Verify all operations are available."""
    try:
        from refactored_sqltools.core.operations.predefined import operation_registry
        operations = operation_registry.list_operations()
        
        expected_operations = [
            "Cancelar Cupom",
            "Apagar Certificado", 
            "Corrigir Erro de Equipamento",
            "Limpar Tabelas do Fisco",
            "Consultar Transações",
            "Consultar Proprio",
            "Consultar NCM Inexistente"
        ]
        
        missing = []
        for op in expected_operations:
            if op not in operations:
                missing.append(op)
        
        if missing:
            print(f"❌ Missing operations: {missing}")
            return False
        
        print(f"✅ All {len(operations)} operations available")
        return True
    except Exception as e:
        print(f"❌ Operations verification error: {e}")
        return False

def verify_database_drivers():
    """Verify database drivers are available."""
    try:
        from refactored_sqltools.core.database.manager import DatabaseManager
        manager = DatabaseManager()
        
        # Check supported types
        supported_types = DatabaseManager.get_supported_databases()
        expected_types = ["Firebird", "SQL Server"]
        
        for db_type in expected_types:
            if db_type not in supported_types:
                print(f"❌ Missing database type: {db_type}")
                return False
            
            # Try to get driver (should not raise exception)
            driver = manager.get_driver(db_type)
            if driver is None:
                print(f"❌ Could not get driver for: {db_type}")
                return False
        
        print(f"✅ All database drivers available: {supported_types}")
        return True
    except Exception as e:
        print(f"❌ Database drivers verification error: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🔍 Verifying SQL SysHub Refactored System...")
    print("=" * 50)
    
    checks = [
        ("Module Imports", verify_imports),
        ("Operations Registry", verify_operations),
        ("Database Drivers", verify_database_drivers),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 System verification PASSED - All components working correctly!")
        return 0
    else:
        print("❌ System verification FAILED - Some components have issues")
        return 1

if __name__ == "__main__":
    exit(main())