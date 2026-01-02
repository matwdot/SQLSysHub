"""
Configuration package.

This package contains configuration management for the application.
"""

from .config_manager import ConfigManager, get_config_manager

__all__ = ['ConfigManager', 'get_config_manager']
