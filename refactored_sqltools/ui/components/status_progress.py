"""
Status Bar Progress Widget

Widget de progresso animado para a barra de status.
Mostra carregamento com animações suaves e feedback visual.
Layout: [Mensagem à esquerda] | [Barra de progresso + % à direita]
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, pyqtSignal, Qt


class StatusProgressWidget(QWidget):
    """Widget de progresso para a barra de status com animações"""
    
    # Signals
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0
        self.target_progress = 0
        self.is_active = False
        self.dots_count = 0
        self.indeterminate_pos = 0
        self.base_message = ""
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # LEFT SIDE: Status icon + message
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #3498db; font-size: 10px;")
        self.status_icon.setFixedWidth(12)
        layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2c3e50; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Spacer to push progress to the right
        layout.addStretch()
        
        # RIGHT SIDE: Progress bar + percentage
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(10)
        self.set_normal_style()
        layout.addWidget(self.progress_bar)
        
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("color: #2c3e50; font-size: 11px; font-weight: bold;")
        self.percent_label.setFixedWidth(40)
        self.percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.percent_label)
        
        # Initially hidden
        self.setVisible(False)
    
    def set_normal_style(self):
        """Set normal progress bar style"""
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #74b9ff, stop:1 #3498db);
            }
        """)
    
    def setup_timers(self):
        """Setup animation timers"""
        # Progress animation timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.animate_progress)
        self.progress_timer.setInterval(30)
        
        # Dots animation timer
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)
        self.dots_timer.setInterval(350)
        
        # Icon pulse timer
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.animate_pulse)
        self.pulse_timer.setInterval(400)
        self.pulse_state = 0
        
        # Indeterminate animation timer
        self.indeterminate_timer = QTimer()
        self.indeterminate_timer.timeout.connect(self.animate_indeterminate)
        self.indeterminate_timer.setInterval(50)
    
    def show_progress(self, message="Processando"):
        """Show progress widget with message"""
        self.base_message = message
        self.status_label.setText(message)
        self.current_progress = 0
        self.target_progress = 0
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.is_active = True
        
        # Clear status bar message and show widget
        parent = self.parent()
        if parent and hasattr(parent, 'clearMessage'):
            parent.clearMessage()
        
        self.setVisible(True)
        
        # Start animations
        self.dots_timer.start()
        self.pulse_timer.start()
        
        # Reset icon and styles
        self.status_icon.setText("●")
        self.set_normal_style()
    
    def hide_progress(self):
        """Hide progress widget"""
        self.is_active = False
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.progress_timer.stop()
        self.indeterminate_timer.stop()
        self.setVisible(False)
        
        # Restore status bar message
        parent = self.parent()
        if parent and hasattr(parent, 'showMessage'):
            parent.showMessage("Pronto")
    
    def set_progress(self, value, message=None):
        """Set progress value with smooth animation"""
        value = max(0, min(100, value))
        self.target_progress = value
        
        # Stop indeterminate mode if running
        if self.indeterminate_timer.isActive():
            self.indeterminate_timer.stop()
            self.progress_bar.setMaximum(100)
        
        if message:
            self.base_message = message
            self.status_label.setText(message)
        
        # Start smooth animation
        if not self.progress_timer.isActive():
            self.progress_timer.start()
    
    def start_indeterminate(self):
        """Start indeterminate progress animation"""
        self.indeterminate_pos = 0
        self.progress_bar.setMaximum(100)
        self.percent_label.setText("...")
        if not self.indeterminate_timer.isActive():
            self.indeterminate_timer.start()
    
    def animate_indeterminate(self):
        """Animate indeterminate progress (bouncing effect)"""
        self.indeterminate_pos = (self.indeterminate_pos + 3) % 200
        
        if self.indeterminate_pos <= 100:
            value = self.indeterminate_pos
        else:
            value = 200 - self.indeterminate_pos
        
        eased_value = int(value * 0.8 + 10)
        self.progress_bar.setValue(eased_value)
    
    def animate_progress(self):
        """Animate progress bar smoothly"""
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
        """Animate loading dots"""
        if not self.is_active:
            return
        
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.status_label.setText(f"{self.base_message}{dots}")
    
    def animate_pulse(self):
        """Animate status icon pulse"""
        if not self.is_active:
            return
        
        colors = ["#3498db", "#74b9ff", "#0984e3", "#74b9ff"]
        self.pulse_state = (self.pulse_state + 1) % len(colors)
        self.status_icon.setStyleSheet(f"color: {colors[self.pulse_state]}; font-size: 10px;")
    
    def set_connecting_state(self):
        """Set to connecting state"""
        self.show_progress("Conectando ao banco de dados")
        self.start_indeterminate()
    
    def set_executing_state(self, operation_name=""):
        """Set to executing state"""
        msg = f"Executando: {operation_name}" if operation_name else "Executando operação"
        self.show_progress(msg)
        self.start_indeterminate()
    
    def set_processing_state(self, message="Processando resultados"):
        """Set to processing state"""
        self.base_message = message
        self.status_label.setText(message)
        self.set_progress(70)
    
    def set_completed_state(self, message="Concluído"):
        """Set to completed state"""
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.indeterminate_timer.stop()
        self.status_label.setText(message)
        self.progress_bar.setMaximum(100)
        self.set_progress(100)
        
        self.status_icon.setText("✓")
        self.status_icon.setStyleSheet("color: #27ae60; font-size: 11px; font-weight: bold;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #27ae60;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background-color: #27ae60;
            }
        """)
        
        QTimer.singleShot(3000, self.hide_progress)
    
    def set_error_state(self, message="Erro na operação"):
        """Set to error state"""
        self.dots_timer.stop()
        self.pulse_timer.stop()
        self.indeterminate_timer.stop()
        self.status_label.setText(message)
        self.progress_bar.setMaximum(100)
        self.set_progress(100)
        
        self.status_icon.setText("✗")
        self.status_icon.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: bold;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e74c3c;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                border-radius: 4px;
                background-color: #e74c3c;
            }
        """)
        
        QTimer.singleShot(5000, self.hide_progress)
