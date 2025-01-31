import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.gui.main_window import MainWindow
from src.gui.login_dialog import LoginDialog
from src.core.database import PasswordVault
from src.utils import resource_path

def initialize_database():
    """Initialize the database if it doesn't exist"""
    data_dir = os.path.dirname(__file__)
    os.makedirs(data_dir, exist_ok=True)
    # db_path = os.path.join(data_dir, 'vault.db')
    vault = PasswordVault("vault.db")
    vault.initialize_database()
    return vault


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    try:
        vault = initialize_database()
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        # icon_path = resource_path(os.path.join(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'lock_icon.png'))
        icon_path = resource_path(os.path.join('resources', 'icons', 'lock_icon.png'))
        app.setWindowIcon(QIcon(icon_path))
        
        login = LoginDialog(vault)
        if login.exec():
            vault.setup_encryption(login.master_password)
            window = MainWindow(vault, login.master_password)
            window.show()
            sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 