# -*- coding: utf-8 -*-
"""
Results Display Component with Fluent Design.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QApplication, QHeaderView, QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QBrush, QColor

from qfluentwidgets import (CardWidget, TableWidget, PushButton, BodyLabel,
                           CaptionLabel, SpinBox, FluentIcon, TextEdit,
                           isDarkTheme)


class _SummaryCard(QWidget):
    """Single summary stat card."""

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.label = CaptionLabel(label_text.upper())
        layout.addWidget(self.label)

        self.value = BodyLabel("--")
        self.value.setStyleSheet("font-size: 26px; font-weight: 700;")
        layout.addWidget(self.value)

        self.sub = CaptionLabel("")
        layout.addWidget(self.sub)

    def setValue(self, value, sub=""):
        self.value.setText(str(value))
        self.sub.setText(sub)


class ResultsDisplay(QWidget):
    """Reusable results display component with Fluent Design."""

    cell_copied = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "text"
        self.last_clicked_item = None
        self.animation_timer = QTimer()
        self.animation_timer.setSingleShot(True)
        self.animation_timer.timeout.connect(self.reset_cell_style)

        self.all_data = []
        self.all_columns = []
        self.current_page = 1
        self.rows_per_page = 100
        self.total_pages = 1
        self._result_title = ""

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.summary_cards = QWidget()
        self.summary_cards.setVisible(False)
        sc_layout = QHBoxLayout(self.summary_cards)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        sc_layout.setSpacing(12)

        self.card_total = _SummaryCard("TOTAL ANALISADO")
        sc_layout.addWidget(self.card_total)

        self.card_warnings = _SummaryCard("AVISOS / ERROS")
        sc_layout.addWidget(self.card_warnings)

        self.card_status = _SummaryCard("STATUS")
        sc_layout.addWidget(self.card_status)

        layout.addWidget(self.summary_cards)

        card = CardWidget()
        self._card = card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._toolbar_widget = QWidget()
        self._toolbar_widget.setFixedHeight(44)
        tb = QHBoxLayout(self._toolbar_widget)
        tb.setContentsMargins(16, 0, 16, 0)

        self.toolbar_title = BodyLabel("Resultados")
        tb.addWidget(self.toolbar_title)

        sep = CaptionLabel("|")
        sep.setContentsMargins(8, 0, 8, 0)
        tb.addWidget(sep)
        sep.setVisible(False)
        self._toolbar_sep = sep

        self.toolbar_subtitle = CaptionLabel("")
        self.toolbar_subtitle.setWordWrap(False)
        tb.addWidget(self.toolbar_subtitle)

        tb.addStretch()

        self.toggle_btn = PushButton(FluentIcon.CODE, "")
        self.toggle_btn.setToolTip("Alternar visualização")
        self.toggle_btn.clicked.connect(self.toggle_display_mode)
        self.toggle_btn.setVisible(False)
        tb.addWidget(self.toggle_btn)

        card_layout.addWidget(self._toolbar_widget)

        self.results_text = TextEdit()
        self.results_text.setFont(QFont("Consolas", 10))
        self.results_text.setReadOnly(True)
        self.results_text.setContentsMargins(16, 8, 16, 8)
        card_layout.addWidget(self.results_text)

        self.results_table = TableWidget()
        self.results_table.setEditTriggers(TableWidget.NoEditTriggers)
        self.results_table.cellClicked.connect(self.copy_cell_to_clipboard)
        self.results_table.setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSortingEnabled(True)
        self.results_table.setSelectionBehavior(TableWidget.SelectItems)
        card_layout.addWidget(self.results_table)

        self._footer_widget = QWidget()
        self._footer_widget.setFixedHeight(36)
        self._footer_widget.setVisible(False)
        fw = QHBoxLayout(self._footer_widget)
        fw.setContentsMargins(16, 0, 16, 0)

        self.footer_info = CaptionLabel("")
        fw.addWidget(self.footer_info)
        fw.addStretch()

        pag = QHBoxLayout()
        pag.setSpacing(4)

        self.prev_btn = PushButton(FluentIcon.LEFT_ARROW, "")
        self.prev_btn.setToolTip("Página anterior")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        pag.addWidget(self.prev_btn)

        self.page_label = CaptionLabel("1 / 1")
        self.page_label.setFixedWidth(50)
        self.page_label.setAlignment(Qt.AlignCenter)
        pag.addWidget(self.page_label)

        self.next_btn = PushButton(FluentIcon.RIGHT_ARROW, "")
        self.next_btn.setToolTip("Próxima página")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pag.addWidget(self.next_btn)

        pag.addWidget(CaptionLabel("|"))

        self.rows_per_page_spin = SpinBox()
        self.rows_per_page_spin.setRange(10, 500)
        self.rows_per_page_spin.setValue(100)
        self.rows_per_page_spin.setSingleStep(50)
        self.rows_per_page_spin.valueChanged.connect(self.change_rows_per_page)
        pag.addWidget(self.rows_per_page_spin)

        pag.addWidget(CaptionLabel("por pág."))

        fw.addLayout(pag)
        card_layout.addWidget(self._footer_widget)

        layout.addWidget(card)

    def display_text_results(self, message):
        self.results_text.setPlainText(message)
        self.current_mode = "text"
        self.toggle_btn.setVisible(False)
        self.results_text.setVisible(True)
        self.results_table.setVisible(False)

    def display_table_results(self, columns, data, message=""):
        self.all_data = data
        self.all_columns = columns
        self.current_page = 1
        self.rows_per_page = self.rows_per_page_spin.value()
        self.total_pages = max(1, (len(data) + self.rows_per_page - 1) // self.rows_per_page)

        if message:
            summary = f"{message}\n\n{len(data)} linhas retornadas."
            self.results_text.setPlainText(summary)
        else:
            self.results_text.setPlainText(f"{len(data)} linhas retornadas.")

        if len(data) > self.rows_per_page:
            self._footer_widget.setVisible(True)
            self.update_pagination_controls()
        else:
            self._footer_widget.setVisible(False)

        self.display_current_page()

        self.toggle_btn.setVisible(True)
        self.current_mode = "table"
        self.results_text.setVisible(False)
        self.results_table.setVisible(True)

    def _footer_info(self, total, elapsed=0):
        self.footer_info.setText(f"Resultados: {total} registros")

    def display_current_page(self):
        if not self.all_data:
            return

        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.all_data))
        page_data = self.all_data[start_idx:end_idx]

        self.results_table.setRowCount(len(page_data))
        self.results_table.setColumnCount(len(self.all_columns))
        self.results_table.setHorizontalHeaderLabels(self.all_columns)

        for row_idx, row in enumerate(page_data):
            for col_idx, val in enumerate(row):
                text = str(val) if val is not None else "NULL"
                item = QTableWidgetItem(text)
                item.setToolTip(text)
                self.results_table.setItem(row_idx, col_idx, item)

        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        for col in range(len(self.all_columns)):
            header.setSectionResizeMode(col, QHeaderView.Interactive)

        self.results_table.resizeColumnsToContents()
        for col in range(len(self.all_columns)):
            current_width = self.results_table.columnWidth(col)
            new_width = max(80, min(300, current_width))
            self.results_table.setColumnWidth(col, new_width)

    def update_pagination_controls(self):
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        self.total_label.setText(f"({len(self.all_data)} reg.)")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination_controls()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination_controls()

    def change_rows_per_page(self, value):
        self.rows_per_page = value
        self.total_pages = max(1, (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page)

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

        if self.all_data:
            if len(self.all_data) > self.rows_per_page:
                self._footer_widget.setVisible(True)
                self.update_pagination_controls()
            else:
                self._footer_widget.setVisible(False)
            self.display_current_page()

    def display_operation_result(self, success, message, result=None):
        self.summary_cards.setVisible(True)
        self._footer_widget.setVisible(False)
        self._toolbar_sep.setVisible(True)

        row_count = 0
        if result and 'data' in result:
            row_count = len(result['data'])

        if success:
            dark = isDarkTheme()
            self.card_total.setValue(str(row_count))
            self.card_warnings.setValue("0")
            self.card_status.setValue("Concluído", "")

            self.toolbar_subtitle.setText(f"{row_count} registros · executado")
            self._footer_info(row_count, 0)

            if result and 'columns' in result:
                cols = result['columns']
                data = result['data']
                self.display_table_results(cols, data, f"{message}")
            else:
                text_message = f"{message}"
                if result and 'rows_affected' in result:
                    text_message += f"\n\nLinhas afetadas: {result['rows_affected']}"
                self.display_text_results(text_message)
        else:
            dark = isDarkTheme()
            self.card_total.setValue("0")
            self.card_warnings.setValue("1")
            self.card_warnings.sub.setText("Falha na execução")
            self.card_status.setValue("Erro", "")

            self.toolbar_subtitle.setText("erro na execução")
            self.display_text_results(f"ERRO\n\n{message}")

    def toggle_display_mode(self):
        if self.current_mode == "text":
            self.current_mode = "table"
            self.results_text.setVisible(False)
            self.results_table.setVisible(True)
            self.toggle_btn.setIcon(FluentIcon.VIEW)
            self.toggle_btn.setToolTip("Mostrar Texto")
        else:
            self.current_mode = "text"
            self.results_text.setVisible(True)
            self.results_table.setVisible(False)
            self.toggle_btn.setIcon(FluentIcon.LIBRARY)
            self.toggle_btn.setToolTip("Mostrar Tabela")

    def copy_cell_to_clipboard(self, row, column):
        item = self.results_table.item(row, column)
        if item:
            text = item.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.animate_cell_click(item)
            self.cell_copied.emit(text)

    def animate_cell_click(self, item):
        if not item:
            return

        if self.last_clicked_item and self.last_clicked_item != item:
            self.reset_cell_style()

        self.last_clicked_item = item
        highlight_color = QColor(52, 152, 219, 40)
        success_color = QColor(46, 204, 113, 30)

        item.setBackground(QBrush(highlight_color))
        QTimer.singleShot(150, lambda: self.transition_to_success_color(item, success_color))
        self.animation_timer.start(600)

    def transition_to_success_color(self, item, success_color):
        if item == self.last_clicked_item:
            item.setBackground(QBrush(success_color))

    def reset_cell_style(self):
        if self.last_clicked_item:
            self.last_clicked_item.setBackground(QBrush())
            self.last_clicked_item = None

    def clear(self):
        self.results_text.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.toggle_btn.setVisible(False)
        self._footer_widget.setVisible(False)
        self.summary_cards.setVisible(False)
        self._toolbar_sep.setVisible(False)

        self.all_data = []
        self.all_columns = []
        self.current_page = 1
        self.total_pages = 1

        self.current_mode = "text"
        self.results_text.setVisible(True)
        self.results_table.setVisible(False)

    def get_text_content(self):
        return self.results_text.toPlainText()

    def get_table_data(self):
        if self.results_table.rowCount() == 0:
            return None

        headers = []
        for col in range(self.results_table.columnCount()):
            header_item = self.results_table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"Column {col}")

        data = []
        for row in range(self.results_table.rowCount()):
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        return {'columns': headers, 'data': data}

    def set_display_mode(self, mode):
        if mode in ["text", "table"] and mode != self.current_mode:
            self.toggle_display_mode()
