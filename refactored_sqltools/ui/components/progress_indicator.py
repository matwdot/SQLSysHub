"""
Progress Indicator Component with Fluent Design.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal

from qfluentwidgets import ProgressBar, CaptionLabel


class ProgressIndicator(QWidget):
    """Reusable progress indicator component with Fluent Design."""

    animation_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0
        self.target_progress = 0
        self.is_animating = False
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_label = CaptionLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def setup_timer(self):
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_progress_animation)
        self.animation_timer.setSingleShot(False)

    def show_progress(self, message="Processando..."):
        self.progress_label.setText(message)
        self.progress_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.current_progress = 0
        self.target_progress = 0
        self.progress_bar.setValue(0)

    def hide_progress(self):
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.stop_animation()

    def set_progress(self, value, message=None):
        value = max(0, min(100, value))

        if message:
            self.progress_label.setText(message)

        self.target_progress = value
        if not self.is_animating and self.current_progress != self.target_progress:
            self.start_animation()

    def start_animation(self):
        if not self.is_animating:
            self.is_animating = True
            self.animation_timer.start(20)

    def stop_animation(self):
        if self.is_animating:
            self.is_animating = False
            self.animation_timer.stop()
            self.animation_finished.emit()

    def update_progress_animation(self):
        if self.current_progress < self.target_progress:
            step = max(1, (self.target_progress - self.current_progress) // 10)
            self.current_progress = min(self.target_progress, self.current_progress + step)
            self.progress_bar.setValue(self.current_progress)

            if self.current_progress >= self.target_progress:
                self.stop_animation()

        elif self.current_progress > self.target_progress:
            step = max(1, (self.current_progress - self.target_progress) // 10)
            self.current_progress = max(self.target_progress, self.current_progress - step)
            self.progress_bar.setValue(self.current_progress)

            if self.current_progress <= self.target_progress:
                self.stop_animation()
        else:
            self.stop_animation()

    def set_connecting_state(self):
        self.show_progress("Conectando ao banco de dados...")
        self.set_progress(30)

    def set_executing_state(self, operation_name=""):
        message = f"Executando {operation_name}..." if operation_name else "Executando operação..."
        self.show_progress(message)
        self.set_progress(20)

    def set_processing_state(self, message="Processando resultados..."):
        self.progress_label.setText(message)
        self.set_progress(80)

    def set_completed_state(self):
        self.progress_label.setText("Concluído!")
        self.set_progress(100)

    def set_error_state(self, message="Erro na operação"):
        self.progress_label.setText(message)
        self.set_progress(100)

    def reset_styles(self):
        pass

    def is_visible(self):
        return self.progress_bar.isVisible()

    def get_current_progress(self):
        return self.current_progress

    def get_target_progress(self):
        return self.target_progress

    def set_indeterminate_mode(self, enabled=True):
        if enabled:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)

    def pulse_animation(self, duration_ms=2000):
        self.show_progress("Aguardando...")

        pulse_timer = QTimer()
        pulse_direction = 1
        pulse_value = 20

        def pulse_update():
            nonlocal pulse_direction, pulse_value
            pulse_value += pulse_direction * 2
            if pulse_value >= 80:
                pulse_direction = -1
            elif pulse_value <= 20:
                pulse_direction = 1
            self.progress_bar.setValue(pulse_value)

        pulse_timer.timeout.connect(pulse_update)
        pulse_timer.start(50)

        stop_timer = QTimer()
        stop_timer.setSingleShot(True)
        stop_timer.timeout.connect(lambda: pulse_timer.stop())
        stop_timer.start(duration_ms)
