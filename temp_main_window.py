# -*- coding: utf-8 -*-
"""
Main Window for SQL SysHub Application

Integrates all UI components into a cohesive interface.
Migrates window setup, styling, and layout from original SQL SysHub.py.
Connects component signals for inter-component communication.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QGroupBox, QPushButton,
                            QLabel, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
import qtawesome as qta

from refactored_sqltools.ui.components.connection_panel import ConnectionPanel
from refactored_sqltools.ui.components.operation_selector import Operation