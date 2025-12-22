# -*- coding: utf-8 -*-
"""
Results Display Component

Extracts results display logic including table and text views.
Implements cell click to clipboard functionality.
Adds toggle between table and text display modes.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QGroupBox, 
                            QPushButton, QApplication)
from PyQt5.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor
import qtawesome as qta


class ResultsDisplay(QWidget):
    """Reusable results display component"""
    
    # Signals
    cell_copied = pyqtSignal(str)  # text copied to clipboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "text"  # "text" or "table"
        self.last_clicked_item = None  # Para controlar a animacao
        self.animation_timer = QTimer()
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self.reset_cell_style)
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Setup the results display UI"""
        layout = QVBoxLayout(self)
        
        # Results group with toggle button
        results_group = QGroupBox("📊 Resultados")
        results_layout = QVBoxLayout(results_group)
        
        # Toggle button for display mode (compact and discrete)
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()  # Push button to the right
        self.toggle_btn = QPushButton()
        table_icon = qta.icon('fa5s.table', color='#7f8c8d')
        self.toggle_btn.setIcon(table_icon)
        self.toggle_btn.setToolTip("Mostrar Tabela")
        self.toggle_btn.clicked.connect(self.toggle_display_mode)
        self.toggle_btn.setVisible(False)  # Initially hidden
        toggle_layout.addWidget(self.toggle_btn)
        results_layout.addLayout(toggle_layout)
        
        # Text display
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Consolas", 9))
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        # Table display
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.cellClicked.connect(self.copy_cell_to_clipboard)
        self.results_table.setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectItems)
        results_layout.addWidget(self.results_table)
        
        layout.addWidget(results_group)
    
    def setup_styles(self):
        """Setup component styles"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #34495e;
            }
            QPushButton {
                background-color: transparent;
                color: #7f8c8d;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 4px;
                font-size: 10px;
                min-width: 20px;
                min-height: 20px;
                max-width: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
                color: #34495e;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #d5dbdb;
                color: #2c3e50;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                color: #2c3e50;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border-bottom: 1px solid #ecf0f1;
                min-height: 16px;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #90caf9;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px 8px;
                border: none;
                font-weight: bold;
                min-height: 24px;
            }
        """)
    
    def display_text_results(self, message):
        """Display text-based results"""
        self.results_text.setPlainText(message)
        self.current_mode = "text"
        self.toggle_btn.setVisible(False)
        self.results_text.setVisible(True)
        self.results_table.setVisible(False)
    
    def display_table_results(self, columns, data, message=""):
        """Display tabular results"""
        # Update text display with summary
        if message:
            summary = f"{message}\n\n📊 {len(data)} linhas retornadas."
            if len(data) > 50:
                summary += f"\n... ({len(data) - 50} linhas omitidas na tabela)"
            self.results_text.setPlainText(summary)
        else:
            self.results_text.setPlainText(f"📊 {len(data)} linhas retornadas.")
        
        # Configure table
        display_rows = min(len(data), 50)  # Limit to 50 rows for performance
        self.results_table.setRowCount(display_rows)
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Populate table data
        for row_idx, row in enumerate(data[:50]):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "NULL")
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content and stretch to fill available space
        self.results_table.resizeColumnsToContents()
        
        # If there are few columns, stretch them to fill the available width
        if len(columns) <= 5:  # For 5 or fewer columns
            header = self.results_table.horizontalHeader()
            header.setStretchLastSection(True)
            # Distribute space more evenly among columns
            for col in range(len(columns)):
                header.setSectionResizeMode(col, header.Stretch)
        else:
            # For many columns, use content-based sizing
            header = self.results_table.horizontalHeader()
            header.setStretchLastSection(False)
            for col in range(len(columns)):
                header.setSectionResizeMode(col, header.ResizeToContents)
        
        # Ensure table fills vertical space when there are few rows
        if display_rows <= 10:  # For 10 or fewer rows
            # Use a timer to adjust row heights after the widget is properly sized
            QTimer.singleShot(100, lambda: self.adjust_row_heights_for_space(display_rows))
        
        # Show toggle button and set initial mode to TABLE (default for tabular data)
        self.toggle_btn.setVisible(True)
        self.current_mode = "table"
        self.results_text.setVisible(False)
        self.results_table.setVisible(True)
        
        # Update toggle button for text mode
        text_icon = qta.icon('fa5s.align-left', color='#7f8c8d')
        self.toggle_btn.setIcon(text_icon)
        self.toggle_btn.setToolTip("Mostrar Texto")
    
    def display_operation_result(self, success, message, result=None):
        """Display operation result (success/error with optional data)"""
        if success:
            if result and 'columns' in result:
                # Table result - show table by default
                cols = result['columns']
                data = result['data']
                self.display_table_results(cols, data, f"✅ SUCESSO\n\n{message}")
            else:
                # Text result
                text_message = f"✅ SUCESSO\n\n{message}"
                if result and 'rows_affected' in result:
                    text_message += f"\n\n📝 Linhas afetadas: {result['rows_affected']}"
                self.display_text_results(text_message)
        else:
            # Error result
            self.display_text_results(f"❌ ERRO\n\n{message}")
    
    def toggle_display_mode(self):
        """Toggle between text and table display modes"""
        if self.current_mode == "text":
            # Switch to table mode
            self.current_mode = "table"
            self.results_text.setVisible(False)
            self.results_table.setVisible(True)
            
            # Update button
            text_icon = qta.icon('fa5s.align-left', color='#7f8c8d')
            self.toggle_btn.setIcon(text_icon)
            self.toggle_btn.setToolTip("Mostrar Texto")
        else:
            # Switch to text mode
            self.current_mode = "text"
            self.results_text.setVisible(True)
            self.results_table.setVisible(False)
            
            # Update button
            table_icon = qta.icon('fa5s.table', color='#7f8c8d')
            self.toggle_btn.setIcon(table_icon)
            self.toggle_btn.setToolTip("Mostrar Tabela")
    
    def adjust_row_heights_for_space(self, row_count):
        """Adjust row heights to fill available vertical space"""
        if row_count <= 0:
            return
            
        # Get available height
        table_height = self.results_table.height()
        header_height = self.results_table.horizontalHeader().height()
        scrollbar_height = 20  # Approximate scrollbar height
        available_height = table_height - header_height - scrollbar_height
        
        if available_height > 0:
            # Calculate optimal row height (minimum 22px, maximum 40px for compact design)
            optimal_height = available_height // row_count
            row_height = max(22, min(40, optimal_height))
            
            # Apply the height to all rows
            for row in range(row_count):
                self.results_table.setRowHeight(row, row_height)
    
    def copy_cell_to_clipboard(self, row, column):
        """Copy clicked cell content to clipboard with elegant animation"""
        item = self.results_table.item(row, column)
        if item:
            text = item.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Aplicar animacao elegante na celula
            self.animate_cell_click(item)
            
            # Emitir sinal
            self.cell_copied.emit(text)
    
    def animate_cell_click(self, item):
        """Animate cell click with subtle pulse effect"""
        if not item:
            return
            
        # Reset previous animation if any
        if self.last_clicked_item and self.last_clicked_item != item:
            self.reset_cell_style()
        
        # Store current item
        self.last_clicked_item = item
        
        # Create a subtle highlight color (light blue with transparency)
        highlight_color = QColor(52, 152, 219, 40)  # Light blue with alpha
        success_color = QColor(46, 204, 113, 30)   # Light green with alpha
        
        # Apply initial highlight (blue for click)
        item.setBackground(QBrush(highlight_color))
        
        # Create timer for color transition to success green
        QTimer.singleShot(150, lambda: self.transition_to_success_color(item, success_color))
        
        # Start timer to reset style
        self.animation_timer.start(600)  # 600ms total duration
    
    def transition_to_success_color(self, item, success_color):
        """Transition to success color"""
        if item == self.last_clicked_item:
            item.setBackground(QBrush(success_color))
    
    def reset_cell_style(self):
        """Reset cell style after animation"""
        if self.last_clicked_item:
            # Reset to transparent background (default)
            self.last_clicked_item.setBackground(QBrush())
            self.last_clicked_item = None
    
    def clear(self):
        """Clear all results"""
        self.results_text.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.toggle_btn.setVisible(False)
        self.current_mode = "text"
        self.results_text.setVisible(True)
        self.results_table.setVisible(False)
    
    def get_text_content(self):
        """Get current text content"""
        return self.results_text.toPlainText()
    
    def get_table_data(self):
        """Get current table data"""
        if self.results_table.rowCount() == 0:
            return None
        
        # Extract headers
        headers = []
        for col in range(self.results_table.columnCount()):
            header_item = self.results_table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"Column {col}")
        
        # Extract data
        data = []
        for row in range(self.results_table.rowCount()):
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        return {'columns': headers, 'data': data}
    
    def set_display_mode(self, mode):
        """Set display mode programmatically"""
        if mode in ["text", "table"] and mode != self.current_mode:
            self.toggle_display_mode()