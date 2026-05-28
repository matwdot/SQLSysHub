"""
Main entry point for the refactored SQL SysHub application.

This module provides the main entry point to launch the refactored
SQL SysHub application with the new modular architecture.
"""

import sys
import argparse
import logging
import os

# Add parent directory to path to allow imports when running directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from refactored_sqltools.ui.windows.main_window import MainWindow
from refactored_sqltools.ui.windows.splash_screen import SplashScreen
from refactored_sqltools.ui.theme_manager import ThemeManager


def setup_logging(debug: bool = False):
    """
    Configure logging for the application.
    
    Args:
        debug: If True, enable debug level logging
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='SQL SysHub - Database Utilities Application',
        prog='sqltools'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='SQL SysHub 2.0 (Refactored)'
    )
    
    parser.add_argument(
        '--style',
        choices=['Fusion', 'Windows', 'WindowsVista'],
        default='Fusion',
        help='Set the application style (default: Fusion)'
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for the SQL SysHub application.
    
    Parses command line arguments, sets up logging, creates the QApplication
    instance and shows the main window with proper cleanup.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting SQL SysHub application...")
    
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("SQL SysHub")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("SQL SysHub")
        
        # Set the requested style
        app.setStyle(args.style)
        logger.info(f"Application style set to: {args.style}")
        
        # Enable high DPI scaling
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Initialize theme before splash screen
        ThemeManager.get_instance()

        # Show splash screen with system checks
        logger.info("Showing splash screen...")
        splash = SplashScreen()
        
        # Variable to hold main window reference
        main_window = None
        
        def on_loading_complete(success: bool):
            nonlocal main_window
            logger.info(f"Loading complete, success: {success}")
            splash.close()
            
            # Create and show main window
            logger.info("Creating main window...")
            main_window = MainWindow()
            
            # Setup cleanup on application quit
            def cleanup():
                logger.info("Cleaning up application resources...")
                if hasattr(main_window, 'cleanup'):
                    main_window.cleanup()
            
            app.aboutToQuit.connect(cleanup)
            main_window.show()
            logger.info("Application started successfully")
        
        splash.loading_complete.connect(on_loading_complete)
        splash.show()
        splash.start_loading()
        
        # Start event loop
        exit_code = app.exec_()
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        
        # Try to show error dialog if possible
        try:
            if 'app' in locals():
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Erro do SQL SysHub")
                msg_box.setText("Falha ao iniciar o SQL SysHub")
                msg_box.setInformativeText(str(e))
                msg_box.setIcon(QMessageBox.Critical)
                
                # Custom OK button
                ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
                
                # Style the message box with theme awareness
                dark = isDarkTheme()
                bg_color = "#2d2d3d" if dark else "white"
                text_color = "#e2e8f0" if dark else "#2c3e50"
                button_bg = "#e74c3c" if not dark else "#c0392b"
                button_hover = "#c0392b" if not dark else "#e74c3c"
                button_pressed = "#a93226" if not dark else "#923121"
                
                msg_box.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {bg_color};
                        color: {text_color};
                        font-size: 12px;
                    }}
                    QMessageBox QLabel {{
                        color: {text_color};
                        padding: 10px;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {button_bg};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 20px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background-color: {button_hover};
                    }}
                    QMessageBox QPushButton:pressed {{
                        background-color: {button_pressed};
                    }}
                """)
                
                msg_box.exec_()
        except Exception:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
