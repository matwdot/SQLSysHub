"""
Enhanced Parameters Widget - Versão Compacta

Componentes compactos para entrada de parâmetros.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                            QCheckBox, QSlider)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QIntValidator

from .styled_calendar import StyledDateEdit, DateRangeWidget


class EnhancedSpinBox(QSpinBox):
    """SpinBox compacto"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 3px 6px;
                background-color: white;
                color: #2c3e50;
                font-size: 10px;
                min-height: 18px;
                max-height: 22px;
            }
            QSpinBox:focus { border: 1px solid #3498db; }
            QSpinBox:hover { border: 1px solid #3498db; }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 14px;
                border: none;
                background-color: #f8f9fa;
                border-radius: 2px;
                margin: 1px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #3498db;
            }
            QSpinBox::up-arrow {
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-bottom: 4px solid #7f8c8d;
                width: 0; height: 0;
            }
            QSpinBox::up-arrow:hover { border-bottom-color: white; }
            QSpinBox::down-arrow {
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #7f8c8d;
                width: 0; height: 0;
            }
            QSpinBox::down-arrow:hover { border-top-color: white; }
        """)


class EnhancedComboBox(QComboBox):
    """ComboBox compacto"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 3px 6px;
                background-color: white;
                color: #2c3e50;
                font-size: 10px;
                min-height: 18px;
                max-height: 22px;
            }
            QComboBox:focus { border: 1px solid #3498db; }
            QComboBox:hover { border: 1px solid #3498db; }
            QComboBox::drop-down {
                width: 18px;
                border: none;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 2px;
                selection-background-color: #3498db;
                font-size: 10px;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                border-radius: 3px;
            }
        """)


class EnhancedLineEdit(QLineEdit):
    """LineEdit compacto"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 3px 6px;
                background-color: white;
                color: #2c3e50;
                font-size: 10px;
                min-height: 18px;
                max-height: 22px;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
            QLineEdit:hover { border: 1px solid #3498db; }
            QLineEdit::placeholder { color: #95a5a6; font-style: italic; }
        """)


class EnhancedCheckBox(QCheckBox):
    """CheckBox compacto"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                font-size: 10px;
                color: #2c3e50;
                spacing: 4px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:hover { border-color: #3498db; }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)


class NumberWithSlider(QWidget):
    """SpinBox com Slider compacto"""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, min_val=1, max_val=1000, default=100, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        self.spinbox = EnhancedSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setValue(default)
        self.spinbox.setFixedWidth(60)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        layout.addWidget(self.spinbox)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.setMaximumHeight(18)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #ecf0f1;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover { background: #2980b9; }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.slider, 1)
    
    def _on_spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)
    
    def _on_slider_changed(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)
        self.valueChanged.emit(value)
    
    def value(self):
        return self.spinbox.value()
    
    def setValue(self, value):
        self.spinbox.setValue(value)
        self.slider.setValue(value)


class ParameterWidgetFactory:
    """Factory para criar widgets de parâmetros compactos"""
    
    @staticmethod
    def create_widget(param_config):
        """Criar widget baseado na configuração"""
        param_type = param_config.get('type', 'text')
        default = param_config.get('default')
        
        if param_type == 'text':
            widget = EnhancedLineEdit()
            if default:
                widget.setText(str(default))
            widget.setPlaceholderText(param_config.get('placeholder', ''))
            if param_config.get('numeric'):
                widget.setValidator(QIntValidator())
            return widget
        
        elif param_type == 'number':
            widget = EnhancedSpinBox()
            widget.setRange(param_config.get('min', 1), param_config.get('max', 999999))
            widget.setSingleStep(param_config.get('step', 1))
            if default:
                widget.setValue(int(default))
            return widget
        
        elif param_type == 'number_slider':
            widget = NumberWithSlider(
                min_val=param_config.get('min', 1),
                max_val=param_config.get('max', 1000),
                default=int(default) if default else 100
            )
            return widget
        
        elif param_type == 'decimal':
            widget = QDoubleSpinBox()
            widget.setRange(param_config.get('min', 0.0), param_config.get('max', 999999.99))
            widget.setDecimals(param_config.get('decimals', 2))
            if default:
                widget.setValue(float(default))
            widget.setStyleSheet(EnhancedSpinBox().styleSheet())
            return widget
        
        elif param_type == 'date':
            widget = StyledDateEdit(show_shortcuts=True)
            if default:
                if default == 'today':
                    widget.setDate(QDate.currentDate())
                elif default == 'month_ago':
                    widget.setDate(QDate.currentDate().addDays(-30))
                elif default == 'week_ago':
                    widget.setDate(QDate.currentDate().addDays(-7))
                elif default == 'year_start':
                    widget.setDate(QDate(QDate.currentDate().year(), 1, 1))
                elif default == 'month_start':
                    today = QDate.currentDate()
                    widget.setDate(QDate(today.year(), today.month(), 1))
                else:
                    widget.setDate(QDate.fromString(default, "yyyy-MM-dd"))
            else:
                widget.setDate(QDate.currentDate())
            return widget
        
        elif param_type == 'date_range':
            return DateRangeWidget()
        
        elif param_type == 'select':
            widget = EnhancedComboBox()
            for option in param_config.get('options', []):
                if isinstance(option, tuple):
                    widget.addItem(option[1], option[0])
                else:
                    widget.addItem(str(option), option)
            if default:
                index = widget.findData(default)
                if index >= 0:
                    widget.setCurrentIndex(index)
            return widget
        
        elif param_type == 'checkbox':
            widget = EnhancedCheckBox(param_config.get('checkbox_label', ''))
            if default:
                widget.setChecked(bool(default))
            return widget
        
        else:
            widget = EnhancedLineEdit()
            if default:
                widget.setText(str(default))
            return widget
    
    @staticmethod
    def get_value(widget, param_type):
        """Obter valor do widget"""
        if param_type == 'text':
            return widget.text().strip()
        elif param_type in ('number', 'decimal'):
            return widget.value()
        elif param_type == 'number_slider':
            return widget.value()
        elif param_type == 'date':
            return widget.date().toString("yyyy-MM-dd")
        elif param_type == 'date_range':
            return {
                'start': widget.getStartDate().toString("yyyy-MM-dd"),
                'end': widget.getEndDate().toString("yyyy-MM-dd")
            }
        elif param_type == 'select':
            return widget.currentData()
        elif param_type == 'checkbox':
            return widget.isChecked()
        else:
            if hasattr(widget, 'text'):
                return widget.text().strip()
            return None
