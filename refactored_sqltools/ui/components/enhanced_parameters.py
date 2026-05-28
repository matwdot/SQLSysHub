"""
Enhanced Parameters Widget - Versão Compacta

Componentes compactos para entrada de parâmetros.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

from qfluentwidgets import (LineEdit, SpinBox, DoubleSpinBox, ComboBox,
                           CheckBox, Slider)

from .styled_calendar import StyledDateEdit, DateRangeWidget


class EnhancedSpinBox(SpinBox):
    """SpinBox compacto"""


class EnhancedComboBox(ComboBox):
    """ComboBox compacto"""


class EnhancedLineEdit(LineEdit):
    """LineEdit compacto"""


class EnhancedCheckBox(CheckBox):
    """CheckBox compacto"""


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
        
        self.value_label = QLabel(str(default))
        self.value_label.setFixedWidth(36)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e74c3c;
            }
        """)
        layout.addWidget(self.value_label)
        
        self.slider = Slider(Qt.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.setMaximumHeight(18)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider, 1)
    
    def _update_value_display(self, value):
        self.value_label.setText(str(value))
    
    def _on_spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self._update_value_display(value)
        self.valueChanged.emit(value)
    
    def _on_slider_changed(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)
        self._update_value_display(value)
        self.valueChanged.emit(value)
    
    def value(self):
        return self.spinbox.value()
    
    def setValue(self, value):
        self.spinbox.setValue(value)
        self.slider.setValue(value)
        self._update_value_display(value)


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
            widget = DoubleSpinBox()
            widget.setRange(param_config.get('min', 0.0), param_config.get('max', 999999.99))
            widget.setDecimals(param_config.get('decimals', 2))
            if default:
                widget.setValue(float(default))
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
