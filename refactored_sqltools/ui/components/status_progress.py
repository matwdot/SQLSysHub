"""
Status Bar Progress Widget with Fluent Design.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal, Qt

from qfluentwidgets import ProgressBar, BodyLabel, CaptionLabel, isDarkTheme


class StatusProgressWidget(QWidget):
    """Widget de progresso para a barra de status com animações."""

    animation_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0
        self.target_progress = 0
        self.is_active = False
        self.dots_count = 0
        self.base_message = ""
        self.setup_ui()
        self.setup_timers()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.status_icon = QLabel("●")
        self.status_icon.setFixedWidth(12)
        layout.addWidget(self.status_icon)

        self.status_label = CaptionLabel("")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.progress_bar = ProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(4)
        layout.addWidget(self.progress_bar)

        self.percent_label = CaptionLabel("0%")
        layout.addWidget(self.percent_label)

        self.setVisible(False)
        
        # Apply initial theme
        self._update_theme()

    def _update_theme(self):
        """Update colors based on current theme"""
        dark = isDarkTheme()
        # Update pulse colors for dark/light theme
        if dark:
            self._pulse_colors = ["#60a5fa", "#3b82f6", "#2563eb", "#3b82f6"]
        else:
            self._pulse_colors = ["#3498db", "#74b9ff", "#0984e3", "#74b9ff"]
            
        # Update success/error colors
        self._success_color = "#4ade80" if dark else "#27ae60"
        self._error_color = "#f87171" if dark else "#e74c3c"
        
        # Update current state if active
        if self.is_active:
            # Reapply current state colors
            current_text = self.status_label.text()
            if "Conectando" in current_text or "Executando" in current_text or "Processando" in current_text:
                # Still in progress state, keep pulse animation
                pass
            elif self.progress_bar.value() == 100:
                if "Concluído" in current_text or self.status_icon.text() == "✓":
                    self.set_completed_state(current_text)
                elif "Erro" in current_text or self.status_icon.text() == "✗":
                    self.set_error_state(current_text)

    def setup_timers(self):
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.animate_progress)
        self.progress_timer.setInterval(30)

        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)
        self.dots_timer.setInterval(350)

        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.animate_pulse)
        self.pulse_timer.setInterval(400)
        self.pulse_state = 0

    def show_progress(self, message="Processando"):
        self.base_message = message
        self.status_label.setText(message)
        self.current_progress = 0
        self.target_progress = 0
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.is_active = True

        self.setVisible(True)

        self.dots_timer.start()
        self.pulse_timer.start()

        self.status_icon.setText("●")

    def hide_progress(self):
        self.is_active = False
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.progress_timer.stop()
        self.setVisible(False)

    def set_progress(self, value, message=None):
        value = max(0, min(100, value))
        self.target_progress = value

        if message:
            self.base_message = message
            self.status_label.setText(message)

        if not self.progress_timer.isActive():
            self.progress_timer.start()

    def animate_progress(self):
        if self.current_progress < self.target_progress:
            diff = self.target_progress - self.current_progress
            step = max(1, int(diff * 0.15))
            self.current_progress = min(self.target_progress, self.current_progress + step)
        elif self.current_progress > self.target_progress:
            diff = self.current_progress - self.target_progress
            step = max(1, int(diff * 0.15))
            self.current_progress = max(self.target_progress, self.current_progress - step)

        self.progress_bar.setValue(self.current_progress)
        self.percent_label.setText(f"{self.current_progress}%")

        if self.current_progress == self.target_progress:
            self.progress_timer.stop()

    def animate_dots(self):
        if not self.is_active:
            return

        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.status_label.setText(f"{self.base_message}{dots}")

    def animate_pulse(self):
        if not self.is_active:
            return

        self.pulse_state = (self.pulse_state + 1) % len(self._pulse_colors)
        self.status_icon.setStyleSheet(f"color: {self._pulse_colors[self.pulse_state]}; font-size: 10px;")

    def set_connecting_state(self):
        self.show_progress("Conectando ao banco de dados")

    def set_executing_state(self, operation_name=""):
        msg = f"Executando: {operation_name}" if operation_name else "Executando operação"
        self.show_progress(msg)

    def set_processing_state(self, message="Processando resultados"):
        self.base_message = message
        self.status_label.setText(message)
        self.set_progress(70)

    def set_completed_state(self, message="Concluído"):
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.status_label.setText(message)
        self.set_progress(100)

        self.status_icon.setText("✓")
        self.status_icon.setStyleSheet(f"color: {self._success_color}; font-size: 11px; font-weight: bold;")

        QTimer.singleShot(3000, self.hide_progress)

    def set_error_state(self, message="Erro na operação"):
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.status_label.setText(message)
        self.set_progress(100)

        self.status_icon.setText("✗")
        self.status_icon.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: bold;")

        QTimer.singleShot(5000, self.hide_progress)
