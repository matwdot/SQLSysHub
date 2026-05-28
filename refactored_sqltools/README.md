# Refactored SQL SysHub

A modular refactoring of the original SQL SysHub.py application, designed with improved architecture, maintainability, and testability.

## Project Structure

```
refactored_sqltools/
├── core/                    # Business logic layer
│   ├── database/           # Database abstraction layer
│   │   ├── manager.py      # Central database manager
│   │   └── drivers/        # Database-specific drivers
│   │       ├── base.py     # Abstract base driver interface
│   │       ├── firebird.py # Firebird database driver
│   │       └── sqlserver.py# SQL Server database driver
│   ├── operations/         # Database operations
│   │   ├── base.py         # Abstract base operation class
│   │   └── predefined.py   # Predefined system operations
│   └── workers/            # Asynchronous workers
│       └── database_worker.py # Database operation worker
├── ui/                      # User interface layer
│   ├── components/         # Reusable UI components
│   │   ├── connection_panel.py  # Database connection panel
│   │   ├── operation_selector.py # Operation selection component
│   │   ├── results_display.py   # Results display component
│   │   └── progress_indicator.py # Progress indicator component
│   └── windows/            # Main application windows
│       └── main_window.py  # Main application window
└── utils/                   # Utility modules
    ├── exceptions.py       # Custom exception classes
    └── validators.py       # Input validation utilities
```

## Design Patterns

- **Strategy Pattern**: Database drivers implement a common interface
- **Template Method**: Operations follow a consistent execution pattern
- **Observer Pattern**: UI components communicate via signals
- **Dependency Injection**: Components are loosely coupled for testability

## Testing

The project uses a dual testing approach:

- **Unit Tests**: Located in `tests/unit/` - test individual components
- **Property-Based Tests**: Located in `tests/property/` - test universal properties using Hypothesis
- **Integration Tests**: Located in `tests/integration/` - test component interactions

### Running Tests

```bash
# Run all tests with the standard library runner
python -m unittest discover -s tests

# Optional, if pytest is installed
python -m pytest
```

## Requirements

- Python 3.8+
- PyQt5 (for UI components)
- pytest (for testing)
- hypothesis (for property-based testing)
- Database drivers as needed (fdb, firebirdsql, pyodbc)
