# Main application style
from PyQt6.QtGui import QFontDatabase
import os

# Load the custom font
def load_custom_fonts():
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'CourierPrime-Regular.ttf')
    QFontDatabase.addApplicationFont(font_path)

MAIN_STYLE = """
QDialog, QMainWindow {
    background-color: #00001B;
}

QLabel {
    background-color: transparent;
}

QLineEdit {
    padding: 5px;
    border: 2px solid #bdc3c7;
    border-radius: 3px;
    background-color: #1E1E1E;
    color: white;
    selection-background-color: #3498db;
    selection-color: white;
}

QLineEdit:focus {
    border-color: #F2F3F4;
    background-color: #1E1E1E;
}

QLineEdit:hover {
    background-color: #02066F;
}

QPushButton {
    padding: 6px 20px;
    background-color: #02066F ;
    color: white;
    border: none;
    border-radius: 3px;
    transition: all 0.3s;
}

QPushButton:hover {
    background-color: #2000B1 ;
    color: #e0e0e0;
}
"""

# Title label style
TITLE_STYLE = """
    font-family: 'Courier Prime', 'Courier New', monospace;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 1px;
    color: #24D46D;
    margin: 5px;
    qproperty-alignment: AlignCenter;
"""

# Alternative version with subtle gradient and shadow
TITLE_STYLE_ENHANCED = """
    font-family: 'Courier Prime', 'Courier New', monospace;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 1px;
    color: #27ae60;  /* Matrix-like green */
    margin: 10px;
    qproperty-alignment: AlignCenter;
    text-shadow: 0px 0px 10px rgba(39, 174, 96, 0.3);  /* Subtle glow effect */
"""

# Password List style
PASSWORD_LIST_STYLE = """
    QListWidget {
        background-color: #1e1e1e;
        border: none;
    }
    QListWidget::item {
        padding: 5px;
        margin: 2px;
    }
    QListWidget::item:hover {
        background-color: #3D3D3D;
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: #2D2D2D;
        border-radius: 4px;
    }
"""

# Main Window style
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #1E1E1E;
        color: white;
    }
    QTableWidget {
        background-color: #2D2D2D;
        color: white;
        border: none;
        gridline-color: #3D3D3D;
    }
    QTableWidget::item {
        padding: 8px;
    }
    QHeaderView::section {
        background-color: #2D2D2D;
        color: white;
        padding: 8px;
        border: none;
    }
    QLineEdit {
        background-color: #3D3D3D;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
    }
"""


# Add Home Label style
HOME_LABEL_STYLE = """
    QLabel {
        color: #808080;
        border: none;
        font-size: 12px;
        padding: 4px;
        margin-top: 16px;
    }
"""

# Categories List style
CATEGORIES_LIST_STYLE = """
    QListWidget {
        background-color: transparent;
        border: none;
        outline: none;
        padding: 0;
    }
    QListWidget::item {
        background-color: transparent;
        padding: 2ram;
        border: none;
    }
    QListWidget::item:selected {
        background-color: #2C2C2C;
        border-radius: 5px;
        border: none;
    }
    QListWidget::item:hover {
        background-color: #2C2C2C;
        border-radius: 5px;
        border: none;
    }
"""

# Categories Label style
CATEGORIES_LABEL_STYLE = """
    QLabel {
        color: white;
    }
"""

DETAILS_CATEGORY_LABEL_STYLE = """
    QLabel {
        color: white;
        font-size: 14px;
        font-weight: bold;
        qproperty-alignment: AlignCenter;
        padding: 5px;
        background-color: #2C2C2C;
        border-radius: 4px;
        margin: 5px;
        min-width: 150px;
    }
"""

# Sidebar Container style
SIDEBAR_CONTAINER_STYLE = """
    QWidget#sidebarContainer {
        background-color: #1E1E1E;
        border-right: 1px solid #3D3D3D;
    }
"""

# Add Button style
ADD_BUTTON_STYLE = """
    QPushButton {
        background-color: #0D6EFD;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #0B5ED7;
    }
    QPushButton:disabled {
        background-color: #6C757D;
    }
"""

# Notes Input style
NOTES_INPUT_STYLE = """
    QTextEdit {
        background-color: #2C2C2C;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px;
    }
"""

# Icon Label style
ICON_LABEL_STYLE = """
    QLabel {
        background-color: transparent;
        border: none;
        padding: 4px;
    }
"""

# Category Button style
CATEGORY_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px;
        text-align: left;
    }
    QPushButton:hover {
        background-color: #3D3D3D;
    }
"""

# Add Category Dialog styles
ADD_CATEGORY_DIALOG_STYLE = """
    QDialog {
        background-color: #1E1E1E;
        color: white;
    }
    QLineEdit {
        background-color: #3D3D3D;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton {
        padding: 8px;
        border-radius: 4px;
    }
    QLabel {
        color: white;
    }
"""

CANCEL_BUTTON_STYLE = """
    QPushButton {
        background-color: #3D3D3D;
        color: white;
        border: none;
    }
    QPushButton:hover {
        background-color: #4D4D4D;
    }
"""

SAVE_BUTTON_STYLE = """
    QPushButton {
        background-color: #0D6EFD;
        color: white;
        border: none;
    }
    QPushButton:hover {
        background-color: #0B5ED7;
    }
"""

# Add Password Dialog styles
ADD_PASSWORD_DIALOG_STYLE = """
    QDialog {
        background-color: #1E1E1E;
        color: white;
    }
    QLabel {
        color: white;
    }
    QLineEdit, QTextEdit, QComboBox {
        background-color: #3D3D3D;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton {
        padding: 8px 16px;
        border-radius: 4px;
        background-color: #0D6EFD;
        color: white;
        border: none;
    }
    QPushButton:hover {
        background-color: #0B5ED7;
    }
"""

# Main Window additional styles
SEARCH_BAR_STYLE = """
    QLineEdit {
        background-color: #3D3D3D;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
    }
"""

DETAIL_PANEL_STYLE = """
    QWidget {
        background-color: #2C2C2C;
        border-radius: 8px;
    }
"""

FAVORITE_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        border: none;
        border-radius: 5px;
        padding: 8px;
        color: #808080;
        font-size: 16px;
    }
    QPushButton:hover {
        background-color: #3C3C3C;
    }
    QPushButton:checked {
        color: #FFD700;
    }
    QPushButton:disabled {
        color: #505050;
    }
"""

CATEGORY_COMBO_STYLE = """
    QComboBox {
        background-color: #2C2C2C;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        color: white;
        min-width: 150px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::disabled {
        color: #505050;
    }
"""

CATEGORY_LABEL_STYLE = """
    QLabel {
        background-color: #2C2C2C;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        color: white;
        min-width: 150px;
    }
"""

# Add missing styles
ACTION_BUTTON_STYLE = """
    QPushButton {
        background-color: #0D6EFD;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
    }
    QPushButton:hover {
        background-color: #0B5ED7;
    }
    QPushButton:disabled {
        background-color: #6C757D;
    }
"""

# Message Box style - Minimal override to keep default theme with white text
MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: #00001B;
    }
    QMessageBox QLabel {
        color: white;
        background-color: transparent;
    }
    QMessageBox QPushButton {
        background-color: #02066F;
        color: white;
        border: none;
        border-radius: 3px;
        min-width: 70px;
    }
    QMessageBox QPushButton:hover {
        background-color: #2000B1;
    }
"""

# Add this new style for category dropdowns
CATEGORY_DROPDOWN_STYLE = """
    QComboBox {
        background-color: #2C2C2C;
        color: white;
        border: 1px solid #3D3D3D;
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 125px;
        font-size: 12px;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 15px;
        width: 30px;
    }
    QComboBox::down-arrow {
        image: url(src/resources/icons/dropdown_arrow.png);
        width: 12px;
        height: 12px;
    }
    QComboBox:hover {
        background-color: #3D3D3D;
        border: 1px solid #4A4A4A;
    }
    QComboBox:disabled {
        color: #808080;
        background-color: #252525;
        border: 1px solid #303030;
    }
    QComboBox QAbstractItemView {
        background-color: #2C2C2C;
        color: white;
        selection-background-color: #02066F;
        selection-color: white;
        border: 1px solid #3D3D3D;
        padding: 4px;
        outline: none;
    }
    QComboBox QAbstractItemView::item {
        min-height: 25px;
        padding: 4px 8px;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #3D3D3D;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #02066F;
    }
"""


