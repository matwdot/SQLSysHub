"""
Styled Calendar Widget with Fluent Design.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                             QPushButton, QLabel, QFrame, QDateEdit, QMenu,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QLocale
from PyQt5.QtGui import QFont, QTextCharFormat, QColor

from qfluentwidgets import PushButton, CaptionLabel, isDarkTheme


class StyledCalendarWidget(QCalendarWidget):
    """Calendário compacto com estilo moderno"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_calendar()
        self.apply_styles()

    def setup_calendar(self):
        self.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        self.setFirstDayOfWeek(Qt.Sunday)
        self.setNavigationBarVisible(True)
        self.highlight_today()

    def highlight_today(self):
        today_format = QTextCharFormat()
        dark = isDarkTheme()
        if dark:
            today_format.setBackground(QColor("#1e3a5f"))  # Dark blue for dark theme
            today_format.setForeground(QColor("#60a5fa"))  # Light blue text
        else:
            today_format.setBackground(QColor("#e8f4fd"))
            today_format.setForeground(QColor("#2980b9"))
        today_format.setFontWeight(QFont.Bold)
        self.setDateTextFormat(QDate.currentDate(), today_format)

    def apply_styles(self):
        dark = isDarkTheme()
        bg_color = "#1e1e2e" if dark else "white"
        nav_bg_start = "#60a5fa" if dark else "#3498db"
        nav_bg_end = "#3b82f6" if dark else "#2980b9"
        button_hover = "rgba(255, 255, 255, 0.1)" if dark else "rgba(255, 255, 255, 0.2)"
        menu_bg = "#2d2d3d" if dark else "white"
        menu_border = "#404040" if dark else "#bdc3c7"
        menu_selected_bg = "#60a5fa" if dark else "#3498db"
        spinbox_bg = "rgba(255, 255, 255, 0.1)" if dark else "rgba(255, 255, 255, 0.9)"
        item_bg = "#2d2d3d" if dark else "white"
        item_disabled = "#888888" if dark else "#bdc3c7"
        item_selection = "#60a5fa" if dark else "#3498db"
        item_selection_hover = "#60a5fa" if dark else "#ebf5fb"
        gridline = "#404040" if dark else "#ecf0f1"
        item_color = "#e2e8f0" if dark else "#2c3e50"
        
        self.setStyleSheet(f"""
            QCalendarWidget {{
                background-color: {bg_color};
                border: none;
                font-size: 10px;
                color: {item_color};
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {nav_bg_start}, stop:1 {nav_bg_end});
                border-radius: 4px 4px 0 0;
                padding: 2px;
                min-height: 24px;
                max-height: 28px;
            }}
            QCalendarWidget QToolButton {{
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 10px;
                font-weight: bold;
                margin: 1px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {button_hover};
            }}
            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {{
                color: white;
                font-size: 10px;
                padding: 2px 6px;
            }}
            QCalendarWidget QMenu {{
                background-color: {menu_bg};
                border: 1px solid {menu_border};
                border-radius: 4px;
                padding: 2px;
                font-size: 10px;
            }}
            QCalendarWidget QMenu::item {{
                padding: 4px 12px;
                border-radius: 3px;
            }}
            QCalendarWidget QMenu::item:selected {{
                background-color: {menu_selected_bg};
                color: white;
            }}
            QCalendarWidget QSpinBox {{
                background-color: {spinbox_bg};
                border: none;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 10px;
                font-weight: bold;
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {item_bg};
                selection-background-color: {item_selection};
                selection-color: white;
                font-size: 10px;
                outline: none;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {item_color};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {item_disabled};
            }}
            QCalendarWidget QTableView {{
                border: none;
                gridline-color: {gridline};
            }}
            QCalendarWidget QTableView::item {{
                padding: 2px;
                border-radius: 3px;
            }}
            QCalendarWidget QTableView::item:hover {{
                background-color: {item_selection_hover};
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {item_selection};
                color: white;
            }}
        """)


class StyledDateEdit(QWidget):
    """Widget de data compacto com calendário estilizado"""

    dateChanged = pyqtSignal(QDate)

    def __init__(self, parent=None, show_shortcuts=True):
        super().__init__(parent)
        self._date = QDate.currentDate()
        self._show_shortcuts = show_shortcuts
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(self._date)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.date_edit.setCalendarWidget(StyledCalendarWidget())
        layout.addWidget(self.date_edit, 1)

        if self._show_shortcuts:
            self.shortcuts_btn = PushButton("...")
            self.shortcuts_btn.setToolTip("Atalhos de data")
            self.shortcuts_btn.setFixedSize(24, 24)
            self.shortcuts_btn.clicked.connect(self._show_shortcuts_menu)
            layout.addWidget(self.shortcuts_btn)
            layout.setAlignment(self.shortcuts_btn, Qt.AlignVCenter)

    def apply_styles(self):
        dark = isDarkTheme()
        border_color = "#bdc3c7" if not dark else "#666666"
        bg_color = "white" if not dark else "#2d2d3d"
        text_color = "#2c3e50" if not dark else "#e2e8f0"
        focus_border = "#3498db" if not dark else "#60a5fa"
        
        self.setStyleSheet(f"""
            QDateEdit {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 3px 6px;
                background-color: {bg_color};
                color: {text_color};
                font-size: 10px;
                min-height: 18px;
                max-height: 22px;
            }}
            QDateEdit:focus {{ border: 1px solid {focus_border}; }}
            QDateEdit:hover {{ border: 1px solid {focus_border}; }}
        """)

    def _show_shortcuts_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
                font-size: 10px;
            }
            QMenu::item {
                padding: 5px 12px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ecf0f1;
                margin: 3px 6px;
            }
        """)

        shortcuts = [
            ("Hoje", QDate.currentDate()),
            ("Ontem", QDate.currentDate().addDays(-1)),
            None,
            ("7 dias", QDate.currentDate().addDays(-7)),
            ("30 dias", QDate.currentDate().addDays(-30)),
            None,
            ("Início mês", QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)),
            ("Início ano", QDate(QDate.currentDate().year(), 1, 1)),
        ]

        for shortcut in shortcuts:
            if shortcut is None:
                menu.addSeparator()
            else:
                label, date = shortcut
                action = menu.addAction(label)
                action.triggered.connect(lambda checked, d=date: self.setDate(d))

        menu.exec_(self.shortcuts_btn.mapToGlobal(self.shortcuts_btn.rect().bottomLeft()))

    def _on_date_changed(self, date):
        self._date = date
        self.dateChanged.emit(date)

    def date(self):
        return self._date

    def setDate(self, date):
        self._date = date
        self.date_edit.setDate(date)

    def setMinimumDate(self, date):
        self.date_edit.setMinimumDate(date)

    def setMaximumDate(self, date):
        self.date_edit.setMaximumDate(date)

    def setDisplayFormat(self, format_str):
        self.date_edit.setDisplayFormat(format_str)


class DateRangeWidget(QWidget):
    """Widget compacto para intervalo de datas"""

    rangeChanged = pyqtSignal(QDate, QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(2)

        for label, start, end in [("Hoje", 0, 0), ("7d", -7, 0), ("30d", -30, 0), ("Mês", "month", 0)]:
            btn = PushButton(label)
            btn.setProperty("preset", True)
            btn.clicked.connect(lambda c, s=start, e=end: self._apply_preset(s, e))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        layout.addLayout(presets_layout)

        dates_layout = QHBoxLayout()
        dates_layout.setSpacing(4)

        self.start_date = StyledDateEdit(show_shortcuts=False)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.dateChanged.connect(self._on_range_changed)
        dates_layout.addWidget(self.start_date)

        dates_layout.addWidget(CaptionLabel("→"))

        self.end_date = StyledDateEdit(show_shortcuts=False)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self._on_range_changed)
        dates_layout.addWidget(self.end_date)

        layout.addLayout(dates_layout)

    def apply_styles(self):
        dark = isDarkTheme()
        preset_bg = "#f8f9fa" if not dark else "#2d2d3d"
        preset_hover = "#3498db" if not dark else "#60a5fa"
        preset_border = "#dfe6e9" if not dark else "#404040"
        preset_color = "#2c3e50" if not dark else "#e2e8f0"
        preset_hover_color = "white" if not dark else "#e2e8f0"
        label_color = "#7f8c8d" if not dark else "#94a3b8"
        
        self.setStyleSheet(f"""
            QPushButton[preset="true"] {{
                background-color: {preset_bg};
                border: 1px solid {preset_border};
                border-radius: 8px;
                padding: 2px 6px;
                font-size: 9px;
                color: {preset_color};
            }}
            QPushButton[preset="true"]:hover {{
                background-color: {preset_hover};
                color: {preset_hover_color};
            }}
            QLabel {{ color: {label_color}; font-size: 10px; }}
        """)

    def _apply_preset(self, start_offset, end_offset):
        today = QDate.currentDate()
        if start_offset == "month":
            start = QDate(today.year(), today.month(), 1)
        else:
            start = today.addDays(start_offset)
        self.start_date.setDate(start)
        self.end_date.setDate(today.addDays(end_offset))

    def _on_range_changed(self):
        self.rangeChanged.emit(self.start_date.date(), self.end_date.date())

    def getStartDate(self):
        return self.start_date.date()

    def getEndDate(self):
        return self.end_date.date()

    def setStartDate(self, date):
        self.start_date.setDate(date)

    def setEndDate(self, date):
        self.end_date.setDate(date)
