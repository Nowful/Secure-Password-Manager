from PyQt6.QtWidgets import (QDialog, QLabel, 
                            QLineEdit, QPushButton, QGridLayout,
                            QTextEdit, QHBoxLayout, QMessageBox, QComboBox)
from src.gui.add_category_dialog import AddCategoryDialog
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from PyQt6.QtGui import QIcon, QPixmap, QMovie
import os
from PyQt6.QtCore import QTimer
from src.resources.styles import (ADD_PASSWORD_DIALOG_STYLE, 
                                CATEGORIES_LABEL_STYLE,
                                CATEGORY_DROPDOWN_STYLE)
from src.utils import resource_path, show_message_box

class AddPasswordDialog(QDialog):
    def __init__(self, vault, master_password):
        super().__init__()
        self.vault = vault
        if not master_password:
            raise ValueError("Master password cannot be None")
        self.master_password = master_password
        
        # Store reference to main window if provided
        self.main_window = None
        
        self.setWindowTitle("Add New Password")
        layout = QGridLayout()
        
        # Website input (row 0)
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("Url (https://www.example.com)")
        self.website_input.textChanged.connect(self.website_input_changed)
        layout.addWidget(QLabel("Website Url:"), 0, 0)
        layout.addWidget(self.website_input, 0, 1)

        # Title and icon (row 1)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Website Title")
        self.title_input.setMaxLength(20) 
        layout.addWidget(QLabel("Title:"), 1, 0)
        layout.addWidget(self.title_input, 1, 1)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        layout.addWidget(self.icon_label, 1, 2)

        # Username (row 2)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email ID")
        layout.addWidget(QLabel("Email ID:"), 2, 0)
        layout.addWidget(self.username_input, 2, 1)
        
        # Password (row 3)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Password:"), 3, 0)
        layout.addWidget(self.password_input, 3, 1)

        # Category dropdown (row 4)
        category_label = QLabel("Category:")
        category_label.setStyleSheet(CATEGORIES_LABEL_STYLE)
        self.category_combo = QComboBox()
        self.category_combo.setPlaceholderText("Select Category (Optional)")
        self.category_combo.setStyleSheet(CATEGORY_DROPDOWN_STYLE)
        self.load_categories()
        layout.addWidget(category_label, 4, 0)
        layout.addWidget(self.category_combo, 4, 1)
        
        # Notes (row 5)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        layout.addWidget(QLabel("Notes:"), 5, 0)
        layout.addWidget(self.notes_input, 5, 1)
        
        # Buttons (row 6)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save")

        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self.save_password)
        save_button.setDefault(True)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout, 6, 0, 1, 2)
        
        self.setLayout(layout)

        # Add timer as instance variable
        self.fetch_timer = QTimer()
        self.fetch_timer.setSingleShot(True)
        self.fetch_timer.timeout.connect(self.fetch_website_info)

        # Setup loading animation
        # self.loading_movie = QMovie(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'loading_icon.gif'))
        self.loading_movie = QMovie(resource_path(os.path.join('resources', 'icons', 'loading_icon.gif')))
        self.loading_movie.setScaledSize(self.icon_label.size())

        # Connect category combo box signal
        self.category_combo.currentIndexChanged.connect(self.handle_category_selection)

        # Apply styles
        self.setStyleSheet(ADD_PASSWORD_DIALOG_STYLE)

    def get_values(self):
        """Return the password data after successful save"""
        return getattr(self, 'password_data', None) 

    def get_website_info(self, url):
        """Extract website title and favicon from URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            parsed_uri = urlparse(url)
            base_domain = parsed_uri.netloc
            favicon_url = f"https://www.google.com/s2/favicons?domain={base_domain}&sz=64"
            icon_response = requests.get(favicon_url, timeout=5)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
            page_response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(page_response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else base_domain

            if icon_response.status_code == 200:
                self.icon_data = icon_response.content
                pixmap = QPixmap()
                pixmap.loadFromData(self.icon_data)
                icon = QIcon(pixmap)
                return title, icon, self.icon_data
            else:
                return self.set_default_icon(url)
            
        except Exception as e:
            print(f"Error fetching website info: {str(e)}")
            return self.set_default_icon(url)

    def set_default_icon(self, url=None):
        """Set default icon when favicon cannot be fetched"""
        # default_icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'web_icon.png')
        default_icon_path = resource_path(os.path.join('resources', 'icons', 'web_icon.png'))
        if os.path.exists(default_icon_path):
            with open(default_icon_path, 'rb') as f:
                self.icon_data = f.read()
            default_icon = QIcon(default_icon_path)
            return url and urlparse(url).netloc or "Unknown", default_icon, self.icon_data
        return None, None, None

    def website_input_changed(self):
        """Handle website URL input changes with debouncing"""
        # Show loading animation
        self.loading_movie.start()
        self.icon_label.setMovie(self.loading_movie)
        
        # Reset and start timer
        self.fetch_timer.stop()
        self.fetch_timer.start(1000)

    def fetch_website_info(self):
        """Fetch website info after delay"""
        url = self.website_input.text().strip()
        if url:
            title, icon, self.icon_data = self.get_website_info(url)
            if title:
                self.title_input.setText(title)
            if icon:
                self.loading_movie.stop()
                self.icon_label.setPixmap(icon.pixmap(16, 16))
        else:
            self.loading_movie.stop()
            
    def load_categories(self):
        """Load existing categories into the combo box"""
        try:
            self.category_combo.clear()
            
            # Get categories
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    SELECT category_names 
                    FROM categories 
                    ORDER BY category_names
                """)
                categories = cursor.fetchall()
                
                # Add "Create New Category" option first
                self.category_combo.addItem("➕ Create New Category")
                
                if categories:
                    self.category_combo.insertSeparator(1)
                    # Add existing categories
                    for category in categories:
                        if category[0]:  # Only add non-empty categories
                            self.category_combo.addItem(category[0])
                else:
                    # Only add "No Category" when there are no categories
                    self.category_combo.insertSeparator(1)
                    self.category_combo.addItem("No Category")
                    
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Error loading categories: {str(e)}")

    def handle_category_selection(self, index):
        """Handle category combo box selection"""
        try:
            selected_text = self.category_combo.currentText()
            
            if selected_text == "➕ Create New Category":
                # Store the previous index
                previous_index = max(0, self.category_combo.currentIndex() - 1)
                
                # Show the add category dialog
                dialog = AddCategoryDialog(self.vault, self.master_password)
                result = dialog.exec()
                
                if result:
                    # Get the new category name and reload
                    new_category = dialog.get_values()['name']
                    self.load_categories()
                    
                    # Select the newly created category
                    index = self.category_combo.findText(new_category)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)
                else:
                    # If cancelled, revert to previous selection
                    self.category_combo.setCurrentIndex(previous_index)
                
                # Force the combo box to reset its state
                self.category_combo.setCurrentIndex(self.category_combo.currentIndex())
                
        except Exception as e:
            print(f"Error handling category selection: {str(e)}")
            self.category_combo.setCurrentIndex(0)

    def on_category_changed(self, index):
        """Handle regular category selection change"""
        try:
            selected_category = self.category_combo.currentText()
            
            if selected_category in ["No Category", "➕ Create New Category"]:
                # Reset to default style
                self.category_combo.setStyleSheet(self.category_combo.styleSheet())
                return
                
            # Get category color
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    SELECT color 
                    FROM categories 
                    WHERE category_names = ?
                """, (selected_category,))
                result = cursor.fetchone()
                
                if result:
                    color = result[0]
                    # Update combo box text color for selected item
                    current_style = self.category_combo.styleSheet()
                    self.category_combo.setStyleSheet(
                        current_style + f"\nQComboBox {{ color: {color}; }}"
                    )
                    
        except Exception as e:
            print(f"Error updating category color: {str(e)}")
    
    def save_password(self):
        try:
            website = self.website_input.text().strip()
            title = self.title_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()
            notes = self.notes_input.toPlainText().strip()
            category = None if self.category_combo.currentText() == "No Category" else self.category_combo.currentText()
            
            # Validate required fields
            if not title or not username or not password:
                show_message_box(self, QMessageBox.Icon.Warning, "Validation Error", 
                    "Title, email ID and password are required fields.")
                return

            # Validate title length
            if len(title) > 20:
                show_message_box(self, QMessageBox.Icon.Warning, "Title Too Long", 
                    "Title must be 20 characters or less. Please shorten the title.")
                return

            # Check for duplicate title
            existing_entry = self.vault.get_entry("vault", title=title)
            if existing_entry:
                show_message_box(self, QMessageBox.Icon.Warning, "Duplicate Title", 
                    "A password entry with this title already exists. Please choose a different title.")
                return
                
            self.vault.add_entry(
                "vault",
                title=title,
                username=username,
                password=password,
                website=website,
                notes=notes,
                icon=getattr(self, 'icon_data', None),
                category=category
            )
            
            self.password_data = {
                'title': title,
                'username': username,
                'icon_data': getattr(self, 'icon_data', None),
                'category': category
            }
            
            # Show success message
            show_message_box(self, QMessageBox.Icon.Information, "Success", 
                f"Password for '{title}' has been saved successfully!")
            
            self.accept()
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to save password: {str(e)}")
 