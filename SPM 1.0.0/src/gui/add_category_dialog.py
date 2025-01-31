from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QLabel, QMessageBox)
from src.resources.styles import (ADD_CATEGORY_DIALOG_STYLE, 
                                CANCEL_BUTTON_STYLE, 
                                SAVE_BUTTON_STYLE)
from src.utils import show_message_box

class AddCategoryDialog(QDialog):
    def __init__(self, vault, master_password):
        super().__init__()
        self.vault = vault
        if not master_password:
            raise ValueError("Master password cannot be None")
        self.master_password = master_password
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Add Category")
        self.setFixedWidth(400)
        self.setStyleSheet(ADD_CATEGORY_DIALOG_STYLE)

        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.setLayout(layout)

        # Category name input
        name_label = QLabel("Category Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter category name")

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save")
        
        cancel_btn.setStyleSheet(CANCEL_BUTTON_STYLE)
        save_btn.setStyleSheet(SAVE_BUTTON_STYLE)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        # Connect buttons
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.accept)

        # Add widgets to layout
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addStretch()
        layout.addLayout(button_layout)

    def get_values(self):
        return {
            'name': self.name_input.text(),
            'color': '#FFD700'  # Default gold color
        }
        
    def save_category(self):
        """Save the category to the database"""
        try:
            name = self.name_input.text().strip()

            # Check empty name - early return
            if not name:
                show_message_box(self, QMessageBox.Icon.Warning, "Validation Error", "Category name cannot be empty!")
                return False

            # Check name length - early return
            if len(name) > 20:
                show_message_box(self, QMessageBox.Icon.Warning, "Title Too Long", 
                    "Category must be 20 characters or less. Please shorten the name.")
                return False

            # Check duplicate - early return
            existing_entry = self.vault.get_entry("categories", category_names=name)
            if existing_entry:
                show_message_box(self, QMessageBox.Icon.Warning, "Duplicate Title", 
                    "A Category entry with this name already exists. Please choose a different name.")
                return False

            # If all checks pass, save the category
            self.vault.add_entry(
                "categories",
                category_names=name,
                color='#FFD700'  # Default gold color
            )
            return True

        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to save the Category: {str(e)}")
            return False

    def reject(self):
        """Override reject to clear input before closing"""
        self.name_input.clear()  # Clear the input field
        super().reject()

    def accept(self):
        """Override accept to validate and save before closing"""
        if self.save_category():
            self.name_input.clear()  # Clear the input field
            super().accept()