# -*- coding: utf-8 -*-
"""
Results Display Component

Extracts results display logic including table and text views.
Implements cell click to clipboard functionality.
Adds toggle between table and text display modes.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QGroupBox, 
                            QPushButton, QApplication, QLabel, QSpinBox)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QBrush, QColor
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
        
        # Pagination data
        self.all_data = []
        self.all_columns = []
        self.current_page = 1
        self.rows_per_page = 100
        self.total_pages = 1
        
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """Setup the results display UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Results group with toggle button
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(8, 8, 8, 8)
        results_layout.setSpacing(6)
        
        # Header com toggle e paginação na mesma linha
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # Paginação (esquerda)
        self.pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(self.pagination_widget)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(4)
        
        # Previous button
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("paginationBtn")
        self.prev_btn.setToolTip("Página anterior")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)
        
        # Page info
        self.page_label = QLabel("1 / 1")
        self.page_label.setObjectName("pageLabel")
        self.page_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.page_label)
        
        # Next button
        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("paginationBtn")
        self.next_btn.setToolTip("Próxima página")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)
        
        # Separador
        sep_label = QLabel("|")
        sep_label.setStyleSheet("color: #bdc3c7; margin: 0 4px;")
        pagination_layout.addWidget(sep_label)
        
        # Records per page (compacto)
        self.rows_per_page_spin = QSpinBox()
        self.rows_per_page_spin.setObjectName("rowsSpinBox")
        self.rows_per_page_spin.setRange(10, 500)
        self.rows_per_page_spin.setValue(100)
        self.rows_per_page_spin.setSingleStep(50)
        self.rows_per_page_spin.setToolTip("Registros por página")
        self.rows_per_page_spin.valueChanged.connect(self.change_rows_per_page)
        pagination_layout.addWidget(self.rows_per_page_spin)
        
        rows_label = QLabel("por pág.")
        rows_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        pagination_layout.addWidget(rows_label)
        
        # Total de registros
        self.total_label = QLabel("")
        self.total_label.setObjectName("totalLabel")
        pagination_layout.addWidget(self.total_label)
        
        self.pagination_widget.setVisible(False)
        header_layout.addWidget(self.pagination_widget)
        
        header_layout.addStretch()
        
        # Toggle button (direita, compacto)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setObjectName("toggleBtn")
        table_icon = qta.icon('fa5s.table', color='#7f8c8d')
        self.toggle_btn.setIcon(table_icon)
        self.toggle_btn.setToolTip("Alternar visualização")
        self.toggle_btn.clicked.connect(self.toggle_display_mode)
        self.toggle_btn.setVisible(False)
        header_layout.addWidget(self.toggle_btn)
        
        results_layout.addWidget(header_widget)
        
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
                font-size: 11px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #34495e;
            }
            
            /* Botões de paginação */
            QPushButton#paginationBtn {
                background-color: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 10px;
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton#paginationBtn:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton#paginationBtn:pressed {
                background-color: #dee2e6;
            }
            QPushButton#paginationBtn:disabled {
                background-color: #f8f9fa;
                color: #ced4da;
                border-color: #e9ecef;
            }
            
            /* Toggle button */
            QPushButton#toggleBtn {
                background-color: transparent;
                color: #6c757d;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton#toggleBtn:hover {
                background-color: #f8f9fa;
                border-color: #adb5bd;
            }
            
            /* Page label */
            QLabel#pageLabel {
                color: #495057;
                font-size: 10px;
                font-weight: bold;
                padding: 0 6px;
                min-width: 50px;
            }
            
            /* Total label */
            QLabel#totalLabel {
                color: #6c757d;
                font-size: 10px;
                margin-left: 8px;
            }
            
            /* Spin box */
            QSpinBox#rowsSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 1px 4px;
                background-color: white;
                color: #495057;
                font-size: 10px;
                min-width: 45px;
                max-width: 50px;
                min-height: 18px;
                max-height: 20px;
            }
            QSpinBox#rowsSpinBox:hover {
                border-color: #adb5bd;
            }
            QSpinBox#rowsSpinBox::up-button, QSpinBox#rowsSpinBox::down-button {
                width: 12px;
            }
            
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
                color: #212529;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
                gridline-color: #e9ecef;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 3px 5px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:hover {
                background-color: #e8f4fc;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px 6px;
                border: none;
                border-right: 1px solid #2c3e50;
                font-weight: bold;
                font-size: 10px;
            }
            QHeaderView::section:hover {
                background-color: #4a6278;
            }
            QToolTip {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 4px 6px;
                border-radius: 2px;
                font-size: 10px;
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
        """Display tabular results with internal pagination"""
        # Store all data for pagination
        self.all_data = data
        self.all_columns = columns
        self.current_page = 1
        self.rows_per_page = self.rows_per_page_spin.value()
        self.total_pages = max(1, (len(data) + self.rows_per_page - 1) // self.rows_per_page)
        
        # Update text display with summary
        if message:
            summary = f"{message}\n\n📊 {len(data)} linhas retornadas."
            self.results_text.setPlainText(summary)
        else:
            self.results_text.setPlainText(f"📊 {len(data)} linhas retornadas.")
        
        # Show pagination controls if needed
        if len(data) > self.rows_per_page:
            self.pagination_widget.setVisible(True)
            self.update_pagination_controls()
        else:
            self.pagination_widget.setVisible(False)
        
        # Display current page
        self.display_current_page()
        
        # Show toggle button and set initial mode to TABLE (default for tabular data)
        self.toggle_btn.setVisible(True)
        self.current_mode = "table"
        self.results_text.setVisible(False)
        self.results_table.setVisible(True)
        
        # Update toggle button for text mode
        text_icon = qta.icon('fa5s.align-left', color='#7f8c8d')
        self.toggle_btn.setIcon(text_icon)
        self.toggle_btn.setToolTip("Mostrar Texto")
    
    def display_current_page(self):
        """Display the current page of data"""
        if not self.all_data:
            return
        
        # Calculate page boundaries
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.all_data))
        page_data = self.all_data[start_idx:end_idx]
        
        # Configure table
        self.results_table.setRowCount(len(page_data))
        self.results_table.setColumnCount(len(self.all_columns))
        self.results_table.setHorizontalHeaderLabels(self.all_columns)
        
        # Populate table data for current page
        for row_idx, row in enumerate(page_data):
            for col_idx, val in enumerate(row):
                text = str(val) if val is not None else "NULL"
                item = QTableWidgetItem(text)
                # Adicionar tooltip com texto completo
                item.setToolTip(text)
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Configurar header para permitir redimensionamento manual
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Usar Interactive para permitir redimensionamento manual pelo usuário
        from PyQt5.QtWidgets import QHeaderView
        for col in range(len(self.all_columns)):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
        
        # Redimensionar colunas para o conteúdo inicialmente
        self.results_table.resizeColumnsToContents()
        
        # Definir largura mínima para cada coluna
        for col in range(len(self.all_columns)):
            current_width = self.results_table.columnWidth(col)
            # Mínimo de 80px, máximo de 300px inicialmente
            new_width = max(80, min(300, current_width))
            self.results_table.setColumnWidth(col, new_width)
    
    def update_pagination_controls(self):
        """Update pagination control states"""
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        self.total_label.setText(f"({len(self.all_data)} reg.)")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination_controls()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination_controls()
    
    def change_rows_per_page(self, value):
        """Change number of rows per page"""
        self.rows_per_page = value
        self.total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)
        
        # Adjust current page if necessary
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # Update display
        if self.all_data:
            if len(self.all_data) > self.rows_per_page:
                self.pagination_widget.setVisible(True)
                self.update_pagination_controls()
            else:
                self.pagination_widget.setVisible(False)
            
            self.display_current_page()
    
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
        self.pagination_widget.setVisible(False)
        
        # Clear pagination data
        self.all_data = []
        self.all_columns = []
        self.current_page = 1
        self.total_pages = 1
        
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