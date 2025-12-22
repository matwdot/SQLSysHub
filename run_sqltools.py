#!/usr/bin/env python3
"""
Launcher script for SQL SysHub application.

This script provides an easy way to launch the SQL SysHub application
from the project root directory.
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the main application
from refactored_sqltools.main import main

if __name__ == "__main__":
    sys.exit(main())