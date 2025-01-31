import os
import sys
from PyQt6.QtWidgets import QMessageBox
from src.resources.styles import MESSAGE_BOX_STYLE

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def show_message_box(parent, icon, title, text):
    """Show a styled message box"""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStyleSheet(MESSAGE_BOX_STYLE)
    return msg.exec()