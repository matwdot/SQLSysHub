"""
Progress Indicator Component

Extracts progress bar and animation logic.
Implements smooth progress updates with timer.
Adds visual feedback for different operation states.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QFont


class ProgressIndicator(QWidget):
    """Reusable progress indicator component"""
    
    # Signals
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0
        self.target_progress = 0
        self.is_animating = False
        self.setup_ui()
        self.setup_styles()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the progress indicator UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress label
        self.progress_label = QLabel()
        self.progress_label.setFont(QFont("Arial", 9))
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
    
    def setup_styles(self):
        """Setup component styles"""
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                background-color: #ecf0f1;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
            QLabel {
                color: #34495e;
                font-weight: bold;
            }
        """)
    
    def setup_timer(self):
        """Setup animation timer"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_progress_animation)
        self.animation_timer.setSingleShot(False)
    
    def show_progress(self, message="Processando..."):
        """Show progress indicator with optional message"""
        self.progress_label.setText(message)
        self.progress_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.current_progress = 0
        self.target_progress = 0
        self.progress_bar.setValue(0)
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.stop_animation()
    
    def set_progress(self, value, message=None):
        """Set progress value with smooth animation"""
        # Clamp value between 0 and 100
        value = max(0, min(100, value))
        
        # Update message if provided
        if message:
            self.progress_label.setText(message)
        
        # Set target and start animation if needed
        self.target_progress = value
        if not self.is_animating and self.current_progress != self.target_progress:
            self.start_animation()
    
    def start_animation(self):
        """Start smooth progress animation"""
        if not self.is_animating:
            self.is_animating = True
            self.animation_timer.start(20)  # 20ms for smooth animation (50 FPS)
    
    def stop_animation(self):
        """Stop progress animation"""
        if self.is_animating:
            self.is_animating = False
            self.animation_timer.stop()
            self.animation_finished.emit()
    
    def update_progress_animation(self):
        """Update progress bar with smooth animation"""
        if self.current_progress < self.target_progress:
            # Animate forward
            step = max(1, (self.target_progress - self.current_progress) // 10)
            self.current_progress = min(self.target_progress, self.current_progress + step)
            self.progress_bar.setValue(self.current_progress)
            
            if self.current_progress >= self.target_progress:
                self.stop_animation()
                
        elif self.current_progress > self.target_progress:
            # Animate backward
            step = max(1, (self.current_progress - self.target_progress) // 10)
            self.current_progress = max(self.target_progress, self.current_progress - step)
            self.progress_bar.setValue(self.current_progress)
            
            if self.current_progress <= self.target_progress:
                self.stop_animation()
        else:
            # Already at target
            self.stop_animation()
    
    def set_connecting_state(self):
        """Set progress to connecting state"""
        self.show_progress("Conectando ao banco de dados...")
        self.set_progress(30)
    
    def set_executing_state(self, operation_name=""):
        """Set progress to executing state"""
        message = f"Executando {operation_name}..." if operation_name else "Executando operação..."
        self.show_progress(message)
        self.set_progress(20)
    
    def set_processing_state(self, message="Processando resultados..."):
        """Set progress to processing state"""
        self.progress_label.setText(message)
        self.set_progress(80)
    
    def set_completed_state(self):
        """Set progress to completed state"""
        self.progress_label.setText("Concluído!")
        self.set_progress(100)
    
    def set_error_state(self, message="Erro na operação"):
        """Set progress to error state"""
        self.progress_label.setText(message)
        self.progress_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                background-color: #ecf0f1;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                border-radius: 3px;
            }
        """)
        self.set_progress(100)
    
    def reset_styles(self):
        """Reset progress bar to normal styles"""
        self.progress_label.setStyleSheet("color: #34495e; font-weight: bold;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                background-color: #ecf0f1;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
    
    def is_visible(self):
        """Check if progress indicator is visible"""
        return self.progress_bar.isVisible()
    
    def get_current_progress(self):
        """Get current progress value"""
        return self.current_progress
    
    def get_target_progress(self):
        """Get target progress value"""
        return self.target_progress
    
    def set_indeterminate_mode(self, enabled=True):
        """Set progress bar to indeterminate mode"""
        if enabled:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)  # Indeterminate mode
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)  # Normal mode
    
    def pulse_animation(self, duration_ms=2000):
        """Create a pulsing animation effect"""
        self.show_progress("Aguardando...")
        
        # Create a simple pulse by animating between 20% and 80%
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
        pulse_timer.start(50)  # Update every 50ms
        
        # Stop pulse after duration
        stop_timer = QTimer()
        stop_timer.setSingleShot(True)
        stop_timer.timeout.connect(lambda: pulse_timer.stop())
        stop_timer.start(duration_ms)