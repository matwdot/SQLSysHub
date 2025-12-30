"""
Predefined database operations - Legacy compatibility module.

This module now imports from the new registry system for backward compatibility.
All operations are now defined in individual modules under the 'individual' package.
"""

# Import the new registry for backward compatibility
from .registry import operation_registry

# Re-export for backward compatibility
__all__ = ['operation_registry']