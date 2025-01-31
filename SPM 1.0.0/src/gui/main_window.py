import os
from io import BytesIO
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,QGridLayout,
                            QTreeView, QListWidget, QLineEdit, QPushButton, 
                            QFormLayout, QTextEdit, QDialog, QListWidgetItem, 
                            QLabel, QMessageBox, QApplication, QComboBox)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon, QFontDatabase
from src.core.encryption import Encryption
from src.gui.add_password_dialog import AddPasswordDialog
from src.gui.add_category_dialog import AddCategoryDialog
from src.resources.styles import (
    MAIN_WINDOW_STYLE,
    PASSWORD_LIST_STYLE,
    CATEGORIES_LIST_STYLE,
    SIDEBAR_CONTAINER_STYLE,
    ACTION_BUTTON_STYLE,
    ICON_LABEL_STYLE,
    CATEGORY_BUTTON_STYLE,
    CATEGORIES_LABEL_STYLE,
    SEARCH_BAR_STYLE,
    HOME_LABEL_STYLE,
    CATEGORY_DROPDOWN_STYLE,
    DETAILS_CATEGORY_LABEL_STYLE
)
from src.utils import resource_path, show_message_box

class MainWindow(QMainWindow):
    def __init__(self, vault, master_password):
        super().__init__()
        self.vault = vault
        self.master_password = master_password
        self.setWindowTitle("Secure Password Manager")
        
        # Add edit mode tracking
        self.edit_mode = False
        
        # Disable window resizing and maximization
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        
        # Initial size without right panel
        self.reset_window_size()
        self.init_ui()

        # Apply styles
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self.password_list.setStyleSheet(PASSWORD_LIST_STYLE)
        self.search_bar.setStyleSheet(SEARCH_BAR_STYLE)

    def init_ui(self):
        # Create password_list first
        self.password_list = QListWidget()
        self.password_list.setStyleSheet(PASSWORD_LIST_STYLE)
        self.password_list.setSpacing(2)
        self.password_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        main_layout.setSpacing(0)  # Remove spacing between panels
        central_widget.setLayout(main_layout)

        # Left Panel (Toolbar)
        left_panel = self.setup_Toolbar_panel()
        main_layout.addWidget(left_panel, 1)

        # Middle Panel (List View)
        middle_panel = self.setup_password_list_panel()
        main_layout.addWidget(middle_panel, 2)

        # Right panels
        self.right_panel_1 = self.setup_details_panel()
        self.right_panel_1.hide()
        main_layout.addWidget(self.right_panel_1)

        self.right_panel_2 = self.setup_trash_panel()
        self.right_panel_2.hide()
        main_layout.addWidget(self.right_panel_2)
        
        # Load the entries and categories
        self.load_vault_entries()
        self.load_categories()
        self.update_trash_count()         # Update the Trash count

    def setup_Toolbar_panel(self):
        sidebar_layout = QVBoxLayout()  # Create the layout first
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(10)

        sidebar_container = QWidget()  # Create the container after layout
        sidebar_container.setFixedWidth(150)  # Set fixed width for sidebar in pixels
        sidebar_container.setLayout(sidebar_layout)  # Set the layout to the container

        # Set container background with only right border
        sidebar_container.setObjectName("sidebarContainer")  # Set an object name for the container
        sidebar_container.setStyleSheet(SIDEBAR_CONTAINER_STYLE)  # Apply the style

        # Replace Home Button with Label using the imported style
        home_label = QLabel("Home")
        home_label.setStyleSheet(HOME_LABEL_STYLE)

        # Main Items List
        self.main_items_list = QListWidget() 
        self.main_items_list.setStyleSheet(CATEGORIES_LIST_STYLE)
        self.main_items_list.setFrameShape(QListWidget.Shape.NoFrame)  # Remove frame
        self.main_items_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Hide scrollbar
        
        # Create main items with initial counts
        main_items = [
            ("🛡️ All Items", "0"),
            ("⭐ Favorites", "0"),
            ("🗑️ Trash", "0")
        ]

        for icon_text, count in main_items:
            item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(5, 2, 5, 2)
            item_widget.setLayout(item_layout)

            label = QLabel(icon_text)
            label.setStyleSheet("color: white; font-size: 14px;")
            count_label = QLabel(count)
            count_label.setStyleSheet("color: #808080; font-size: 14px;")

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(count_label)

            item.setSizeHint(item_widget.sizeHint())
            self.main_items_list.addItem(item)
            self.main_items_list.setItemWidget(item, item_widget)

        # Categories Header
        categories_header = QWidget()
        categories_layout = QHBoxLayout()
        categories_layout.setContentsMargins(0, 0, 0, 0)  # Set all margins to 0
        categories_header.setLayout(categories_layout)

        categories_label = QLabel("Categories")
        categories_label.setStyleSheet(CATEGORIES_LABEL_STYLE)
        
        # Create buttons directly in the header layout
        add_category_btn = QPushButton("+")
        delete_category_btn = QPushButton("-")
        for btn in [add_category_btn, delete_category_btn]:
            btn.setStyleSheet(CATEGORY_BUTTON_STYLE)
            btn.setFixedWidth(25)  # Set a fixed width for the buttons
        
        add_category_btn.clicked.connect(self.add_category_dialog)
        delete_category_btn.clicked.connect(self.delete_selected_category)
        
        # Add widgets directly to categories_layout with no spacing
        categories_layout.addWidget(categories_label)
        categories_layout.addStretch()
        categories_layout.addWidget(add_category_btn)
        categories_layout.addWidget(delete_category_btn)
        categories_layout.setSpacing(5)  # Add small spacing between elements

        # Categories List
        self.categories_list = QListWidget()
        self.categories_list.setStyleSheet(CATEGORIES_LIST_STYLE)
        self.categories_list.setFrameShape(QListWidget.Shape.NoFrame)  # Remove frame
        self.categories_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Hide scrollbar

        # Add widgets to main layout
        sidebar_layout.addWidget(home_label)
        sidebar_layout.addWidget(self.main_items_list)
        sidebar_layout.addWidget(categories_header)
        sidebar_layout.addWidget(self.categories_list)
        sidebar_layout.addStretch()

        # Store the current filter state
        self.current_filter = None
        self.current_filter_type = None
        
        # Connect selection signals with proper handling
        self.main_items_list.itemClicked.connect(self.on_sidebar_item_selected)
        self.categories_list.itemClicked.connect(self.on_sidebar_item_selected)

        return sidebar_container

    def add_category_dialog(self):
        """Show dialog to add new category and refresh all category dropdowns"""
        try:
            if not self.master_password:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", "Master password is not set")
                return
            
            # Store current category before making changes
            current_category = None
            if hasattr(self, 'right_panel_1') and self.right_panel_1.isVisible():
                current_category = self.category_label.text()
            
            dialog = AddCategoryDialog(self.vault, self.master_password)
            if dialog.exec() == 1:
                values = dialog.get_values()
                if values:
                    # Add category to sidebar
                    self.add_category_to_list(values)
                    
                    # Refresh all category dropdowns
                    self.load_categories()
                    
                    # Update right panel category combo if it exists and is visible
                    if hasattr(self, 'right_panel_1') and self.right_panel_1.isVisible():
                        self.categories_combo.clear()
                        self.categories_combo.addItem("No Category")
                        
                        with self.vault.conn:
                            cursor = self.vault.conn.cursor()
                            cursor.execute("""
                                SELECT category_names 
                                FROM categories 
                                ORDER BY category_names
                            """)
                            categories = cursor.fetchall()
                            
                            for category in categories:
                                if category[0]:  # Only add non-empty categories
                                    self.categories_combo.addItem(category[0])
                    
                    # Restore the current category selection if it exists
                    if current_category:
                        index = self.categories_combo.findText(current_category)
                        if index >= 0:
                            self.categories_combo.setCurrentIndex(index)
                
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to show add category dialog: {str(e)}")

    def add_category_to_list(self, category_data):
        """Add a category to the sidebar list"""
        item = QListWidgetItem()
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(5, 2, 5, 2)
        item_widget.setLayout(item_layout)

        label = QLabel(category_data['name'])
        label.setStyleSheet("color: white; font-size: 14px;")  # Use white color for all categories
        count_label = QLabel("0")
        count_label.setStyleSheet("color: #808080; font-size: 14px;")

        item_layout.addWidget(label)
        item_layout.addStretch()
        item_layout.addWidget(count_label)

        item.setSizeHint(item_widget.sizeHint())
        self.categories_list.addItem(item)
        self.categories_list.setItemWidget(item, item_widget)

    def delete_selected_category(self):
        """Delete the selected category from both UI and database"""
        current_item = self.categories_list.currentItem()
        if not current_item:
            return
        
        # Get the category name from the item widget
        category_widget = self.categories_list.itemWidget(current_item)
        category_name = category_widget.layout().itemAt(0).widget().text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f'Are you sure you want to delete the category "{category_name}"?\n\n'
            'Note: This will not delete any passwords in this category.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete from database
                with self.vault.conn:
                    cursor = self.vault.conn.cursor()
                    cursor.execute("DELETE FROM categories WHERE category_names = ?", (category_name,))
                    
                    # Update passwords in this category to have no category
                    cursor.execute("UPDATE vault SET category = NULL WHERE category = ?", (category_name,))
                
                # Remove from UI
                self.categories_list.takeItem(self.categories_list.row(current_item))
                
                # Remove from combo box
                index = self.categories_combo.findText(category_name)
                if index >= 0:
                    self.categories_combo.removeItem(index)
                    
                show_message_box(self, QMessageBox.Icon.Information, "Success", "Category deleted successfully!")
                
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to delete category: {str(e)}")

    def update_category_counts(self):
        """Update the counts for each category in the sidebar"""
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("SELECT category_names FROM categories")
                categories = cursor.fetchall()
                
                print("Categories found in database:", categories)  # Debugging output
                
                for category in categories:
                    category_name = category[0]
                    
                    # Get the count of active entries in this category
                    cursor.execute("""
                        SELECT COUNT(*) FROM vault 
                        WHERE category = ? AND deleted = 0
                    """, (category_name,))
                    count = cursor.fetchone()[0]
    
                    # Debugging output
                    print(f"Category: {category_name}, Count: {count}")
        
                    # Find the corresponding category item in the sidebar
                    for i in range(self.categories_list.count()):
                        item = self.categories_list.item(i)
                        item_widget = self.categories_list.itemWidget(item)
                        label = item_widget.layout().itemAt(0).widget().text()
    
                        if label == category_name:
                            count_label = item_widget.layout().itemAt(2).widget()  # Get count label
                            count_label.setText(str(count))
                            break
    
        except Exception as e:
            print(f"Error updating category counts: {str(e)}")           

    def setup_password_list_panel(self):
        middle_panel = QWidget()
        middle_panel.setFixedWidth(300)  # Fixed width in pixels
        
        layout = QVBoxLayout()
        middle_panel.setLayout(layout)

        # Search container
        search_container = QWidget()
        search_layout = QHBoxLayout()
        search_container.setLayout(search_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search Vault")
        self.search_bar.textChanged.connect(self.search_entries)  # Connect to search function
        add_button = QPushButton("+")
        add_button.setStyleSheet(ACTION_BUTTON_STYLE)
        add_button.clicked.connect(self.add_password_dialog)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(add_button)

        # Create a container for the password list and message
        list_container = QWidget()
        list_layout = QVBoxLayout()
        list_container.setLayout(list_layout)

        # Password list
        self.password_list = QListWidget()
        self.password_list.setStyleSheet(PASSWORD_LIST_STYLE)
        self.password_list.setSpacing(2)
        self.password_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.password_list.setWordWrap(True)
        self.password_list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        
        # No results message
        self.no_results_widget = QWidget()
        no_results_layout = QVBoxLayout()
        self.no_results_widget.setLayout(no_results_layout)
        
        self.no_results_icon = QLabel("📝")
        self.no_results_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_icon.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 48px;
                margin-bottom: 10px;
            }
        """)
        
        self.no_results_label = QLabel()
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setWordWrap(True)
        self.no_results_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 14px;
            }
        """)
        
        no_results_layout.addStretch()
        no_results_layout.addWidget(self.no_results_icon)
        no_results_layout.addWidget(self.no_results_label)
        no_results_layout.addStretch()
        
        self.no_results_widget.hide()  # Hidden by default

        # Add widgets to layouts
        list_layout.addWidget(self.password_list)
        list_layout.addWidget(self.no_results_widget)
        
        layout.addWidget(search_container)
        layout.addWidget(list_container)
        
        # Connect password list selection to handler
        self.password_list.itemClicked.connect(self.on_password_selected)
        
        return middle_panel

    def search_entries(self, search_text):
        """Search through password entries"""
        try:
            # Clear current list
            self.password_list.clear()
            
            if not search_text.strip():
                # If search is empty, reload all entries with current filter
                self.load_vault_entries(
                    category=self.current_filter if self.current_filter_type == "category" else None,
                    filter_type=self.current_filter_type
                )
                return
            
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                
                # Prepare search query based on current filter
                if self.current_filter_type == "trash":
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE deleted = 1 
                        AND (title LIKE ? OR username LIKE ? OR website LIKE ?)
                        ORDER BY title
                    """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
                elif self.current_filter_type == "favorites":
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE favorite = 1 AND deleted = 0 
                        AND (title LIKE ? OR username LIKE ? OR website LIKE ?)
                        ORDER BY title
                    """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
                elif self.current_filter_type == "category":
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE category = ? AND deleted = 0 
                        AND (title LIKE ? OR username LIKE ? OR website LIKE ?)
                        ORDER BY title
                    """, (self.current_filter, f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
                else:
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE deleted = 0 
                        AND (title LIKE ? OR username LIKE ? OR website LIKE ?)
                        ORDER BY title
                    """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
                
                entries = cursor.fetchall()
                
                # Handle no results
                if not entries:
                    self.password_list.hide()
                    self.no_results_label.setText("No matching passwords found")
                    self.no_results_widget.show()
                else:
                    self.no_results_widget.hide()
                    self.password_list.show()
                    for icon_data, title, username in entries:
                        self.add_password_to_list({
                            'icon_data': icon_data,
                            'title': title,
                            'username': username
                        })
                    
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to search entries: {str(e)}")

    def add_password_dialog(self):
        try:
            if not self.master_password:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", "Master password is not set")
                return
            dialog = AddPasswordDialog(self.vault, self.master_password)
            if dialog.exec() == 1:
                values = dialog.get_values()
                if values:
                    self.load_vault_entries()  # Refresh the password list
                    self.load_categories()     # Refresh categories and counts
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to create password dialog: {str(e)}")
    
    def load_vault_entries(self, category=None, filter_type=None):
        """Load vault entries with filtering and empty state handling"""
        self.password_list.clear()
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                
                # Prepare query based on filter
                if filter_type == "favorites":
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE favorite = 1 AND deleted = 0
                        ORDER BY title
                    """)
                    filter_description = "favorite passwords"
                    empty_message = "No favorite passwords yet"
                    action_message = "Click the star icon while editing to mark items as favorites"
                elif filter_type == "trash":
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE deleted = 1
                        ORDER BY title
                    """)
                    filter_description = "deleted passwords"
                    empty_message = "Trash is empty"
                    action_message = "Deleted passwords will appear here"
                elif category and category not in ["🛡️ All Items", "⭐ Favorites", "🗑️ Trash"]:
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE category = ? AND deleted = 0
                        ORDER BY title
                    """, (category,))
                    filter_description = f"passwords in {category}"
                    empty_message = f"No passwords in {category}"
                    action_message = "Add a new password and select this category"
                else:
                    cursor.execute("""
                        SELECT icon, title, username 
                        FROM vault 
                        WHERE deleted = 0
                        ORDER BY title
                    """)
                    filter_description = "passwords"
                    empty_message = "No passwords yet"
                    action_message = "Click the + button to add your first password"
                    
                entries = cursor.fetchall()
                
                # Handle empty state
                if not entries:
                    self.password_list.hide()
                    self.no_results_label.setText(f"{empty_message}\n\n{action_message}")
                    self.no_results_widget.show()
                else:
                    self.no_results_widget.hide()
                    self.password_list.show()
                    for icon_data, title, username in entries:
                        self.add_password_to_list({
                            'icon_data': icon_data,
                            'title': title,
                            'username': username
                        })
                    
                # Update counts
                self.update_total_count()
                self.update_favorites_count()
                
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to load vault entries: {str(e)}")

    def update_total_count(self):
        """Update the total count in All Items"""
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM vault WHERE deleted = 0")
                total_count = cursor.fetchone()[0]
                
                # Update the count in the first item (All Items)
                all_items_item = self.main_items_list.item(0)
                if all_items_item:
                    item_widget = self.main_items_list.itemWidget(all_items_item)
                    if item_widget:
                        count_label = item_widget.layout().itemAt(2).widget()  # Get count label
                        count_label.setText(str(total_count))
                        
        except Exception as e:
            print(f"Error updating total count: {str(e)}")

    def add_password_to_list(self, password_data):
        if not password_data:
            return
        
        item = QListWidgetItem()
        item.password_data = password_data
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(10, 8, 10, 8)
        item_widget.setLayout(item_layout)

        # Icon/Logo container
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setStyleSheet(ICON_LABEL_STYLE)
        
        if 'icon_data' in password_data and password_data['icon_data']:
            pixmap = QtGui.QPixmap()
            if pixmap.loadFromData(password_data['icon_data']):
                icon_label.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.set_default_icon(icon_label)
        else:
            self.set_default_icon(icon_label)
        
        # Text container with only title
        text_container = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(10, 0, 0, 0)
        text_container.setLayout(text_layout)
        
        title_label = QLabel(password_data['title'])
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        text_layout.addWidget(title_label)

        item_layout.addWidget(icon_label)
        item_layout.addWidget(text_container, 1)  # Give text container stretch priority

        item.setSizeHint(item_widget.sizeHint())
        self.password_list.addItem(item)
        self.password_list.setItemWidget(item, item_widget)

    def set_default_icon(self, icon_label):
        try:
            # default_icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'web_icon.png')
            default_icon_path = resource_path(os.path.join('resources', 'icons', 'web_icon.png'))
            pixmap = QtGui.QPixmap(default_icon_path)
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            print(f"Error - Unable to set default icon: {str(e)}")
    
    def reset_window_size(self):
        """Reset window size to original dimensions without right panel"""
        initial_width = 150 + 300 + 5  # sidebar + middle + margins
        self.setMinimumSize(initial_width, 500)
        self.resize(initial_width, self.height())

    def on_password_selected(self, item):
        """Handle password selection from the list"""
        if not item or not hasattr(item, 'password_data'):
            return
        
        # Check if in edit mode
        if self.edit_mode:
            reply = QMessageBox.question(
                self,
                'Cancel Edit?',
                'You have unsaved changes. Do you want to cancel editing?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                # Revert selection
                self.password_list.blockSignals(True)
                self.password_list.setCurrentItem(self.password_list.currentItem())
                self.password_list.blockSignals(False)
                return
            else:
                # Exit edit mode
                self.restore_view_mode()
        
        # Continue with password selection
        selected_title = item.password_data['title']
        current_title = self.detail_title.text() if hasattr(self, 'detail_title') else None
        
        # Check if clicking the same password (using title comparison)
        if current_title and selected_title == current_title and self.right_panel_1.isVisible():
            # Close both panels 
            self.right_panel_1.hide()
            self.right_panel_2.hide()
            self.clear_right_panel()
            self.reset_window_size()
            # Clear selection and block signals temporarily to prevent recursive calls
            self.password_list.blockSignals(True)
            self.password_list.clearSelection()
            self.password_list.blockSignals(False)
            return
        
        # Check if the selected item is from the Trash
        if self.current_filter_type == "trash":
            self.right_panel_1.hide()  # Hide details panel
            self.update_trash_details(item)
            self.right_panel_2.show()  # Show trash panel
            new_width = 150 + 300 + 400 + 5  # sidebar + middle + trash_panel + margin
            self.setMinimumSize(new_width, 500)
            self.resize(new_width, self.height())
            return
        
        # Handle normal password selection
        try:
            entry = self.vault.get_entry("vault", title=selected_title)
            if entry:
                # Hide trash panel and show details panel
                self.right_panel_2.hide()
                self.right_panel_1.show()
                new_width = 150 + 300 + 400 + 5  # sidebar + middle + details_panel + margin
                self.setMinimumSize(new_width, 500)
                self.resize(new_width, self.height())
                
                # Process entry data
                password_data = {
                    'title': entry.get('title', ''),
                    'username': entry.get('username', ''),
                    'password': entry.get('password', ''),
                    'website': entry.get('website', ''),
                    'notes': entry.get('notes', ''),
                    'category': entry.get('category'),
                    'icon_data': entry.get('icon')
                }
                
                # Update all fields with the processed data
                self.update_password_details(password_data)
                
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to load password details: {str(e)}")

    def is_trash_item(self, item):
        """Check if the selected item is from the Trash based on the deleted column."""
        title = item.password_data['title']  # Assuming title is used to identify the item
        
        with self.vault.conn:  # Use the vault's database connection
            cursor = self.vault.conn.cursor()
            cursor.execute("SELECT deleted FROM vault WHERE title = ?", (title,))
            result = cursor.fetchone()
            
            if result:
                return result[0] == 1  # Return True if deleted is 1, meaning it's in Trash
        return False  # Default to False if the item is not found

    def setup_details_panel(self):
        details_panel = QWidget()
        details_panel.setFixedWidth(400)  # Fixed width in pixels
        
        layout = QVBoxLayout()
        details_panel.setLayout(layout)
        layout.setContentsMargins(0, 20, 20, 5)  # Adjusted right margin
        layout.setSpacing(20)
        
        # Action Buttons at top
        action_buttons = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_buttons.setLayout(action_layout)

        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑️ Delete")

        # Category label and combo box in action buttons
        self.category_label = QLabel()
        self.category_label.setStyleSheet(DETAILS_CATEGORY_LABEL_STYLE)
        
        self.categories_combo = QComboBox()
        self.categories_combo.setPlaceholderText("Select Category (Optional)")
        self.categories_combo.setStyleSheet(CATEGORY_DROPDOWN_STYLE)
        self.categories_combo.hide()  # Initially hidden

        action_layout.addStretch()
        action_layout.addWidget(self.category_label)
        action_layout.addWidget(self.categories_combo)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)

        # Header with icon, title and favorite
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        header.setLayout(header_layout)

        # Left side - Icon and Title
        icon_title_widget = QWidget()
        icon_title_layout = QHBoxLayout()
        icon_title_layout.setContentsMargins(0, 0, 0, 0)
        icon_title_widget.setLayout(icon_title_layout)

        self.detail_icon = QLabel()
        self.detail_icon.setFixedSize(48, 48)
        self.detail_icon.setStyleSheet("QLabel { background-color: #1C1C1C; border-radius: 8px; }")

        title_widget = QWidget()
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_widget.setLayout(title_layout)

        # Modify title label to handle long text
        self.detail_title = QLabel("Title")
        self.detail_title.setStyleSheet("""
            QLabel { 
                color: white; 
                font-size: 20px; 
                font-weight: bold;
                qproperty-wordWrap: true;  /* Enable word wrap */
                max-width: 300px;          /* Limit width */
                text-overflow: ellipsis;   /* Show ... when text is too long */
            }
        """)
        self.detail_title.setMaximumWidth(300)
        title_layout.addWidget(self.detail_title)

        icon_title_layout.addWidget(self.detail_icon)
        icon_title_layout.addSpacing(10)
        icon_title_layout.addWidget(title_widget)
        icon_title_layout.addStretch()

        # Favorite button with initial state
        self.favorite_btn = QPushButton("☆")  # Start with empty star
        self.favorite_btn.setFixedSize(36, 36)
        self.favorite_btn.setCheckable(True)
        self.favorite_btn.setStyleSheet("""
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
        """)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        self.favorite_btn.setEnabled(False)

        header_layout.addWidget(icon_title_widget)
        header_layout.addWidget(self.favorite_btn)

        # Details form
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-radius: 8px;
            }
        """)
        form = QFormLayout()
        form.setSpacing(15)
        form.setContentsMargins(20, 20, 20, 20)
        form_widget.setLayout(form)

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setObjectName("emailId_input")
        self.username_input.setReadOnly(True)
        self.username_input.setPlaceholderText("Email ID")
        
        # Password field with toggle
        password_container = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_input")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setReadOnly(True)
        self.password_input.setPlaceholderText("Password")
        
        self.toggle_password_btn = QPushButton("👁️")
        self.toggle_password_btn.setFixedSize(36, 36)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4C4C4C;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_btn.setEnabled(False)

        self.copy_password_btn = QPushButton("📋")
        self.copy_password_btn.setFixedSize(36, 36)
        self.copy_password_btn.setStyleSheet(self.toggle_password_btn.styleSheet())
        self.copy_password_btn.clicked.connect(self.copy_password_to_clipboard)
        self.copy_password_btn.setEnabled(False)
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.toggle_password_btn)
        password_container.addWidget(self.copy_password_btn)
        
        # Website field with navigation button
        website_container = QHBoxLayout()
        self.website_input = QLineEdit()
        self.website_input.setObjectName("website_input")
        self.website_input.setReadOnly(True)
        self.website_input.setPlaceholderText("Website")
        
        self.visit_website_btn = QPushButton("🌐")
        self.visit_website_btn.setFixedSize(36, 36)
        self.visit_website_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4C4C4C;
            }
            QPushButton:disabled {
                background-color: #2C2C2C;
                color: #505050;
            }
        """)
        self.visit_website_btn.clicked.connect(self.open_website)
        self.visit_website_btn.setEnabled(False)
        
        website_container.addWidget(self.website_input)
        website_container.addWidget(self.visit_website_btn)
        
        # Notes field
        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("notes_input")
        self.notes_input.setReadOnly(True)
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setMinimumHeight(100)

        # Style all input fields
        input_style = """
            QLineEdit, QTextEdit {
                background-color: #1C1C1C;
                border: none;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            QLineEdit:disabled, QTextEdit:disabled {
                background-color: #2C2C2C;
                color: #505050;
            }
        """
        for widget in [self.username_input, self.password_input, self.website_input, self.notes_input]:
            widget.setStyleSheet(input_style)

        # Add form fields with labels
        label_style = "QLabel { color: #808080; font-size: 14px; }"
        username_label = QLabel("Email ID")
        password_label = QLabel("Password")
        website_label = QLabel("Website")
        notes_label = QLabel("Notes")
        
        for label in [username_label, password_label, website_label, notes_label]:
            label.setStyleSheet(label_style)

        form.addRow(username_label, self.username_input)
        form.addRow(password_label, password_container)
        form.addRow(website_label, website_container)  # Use website_container instead of website_input
        form.addRow(notes_label, self.notes_input)

        # Connect buttons
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.delete_btn.clicked.connect(self.delete_current_entry)
        self.favorite_btn.clicked.connect(self.toggle_favorite)

        # Add everything to main layout
        layout.addWidget(action_buttons)
        layout.addWidget(header)
        layout.addWidget(form_widget)
        layout.addStretch()
        
        return details_panel

    def copy_password_to_clipboard(self):
        """Copy password to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_input.text())
        
    def toggle_favorite(self):
        """Toggle favorite status of current password"""
        try:
            current_title = self.detail_title.text()
            is_favorite = self.favorite_btn.isChecked()
            
            # Update the database
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    UPDATE vault 
                    SET favorite = ? 
                    WHERE title = ?
                """, (is_favorite, current_title))
                
                self.vault.conn.commit()
            
            # Update button text and style based on state
            self.favorite_btn.setText("⭐" if is_favorite else "☆")
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    color: """ + ("#FFD700" if is_favorite else "#808080") + """;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #3C3C3C;
                }
                QPushButton:disabled {
                    color: #505050;
                }
            """)
            
            # Update favorites count in sidebar
            self.update_favorites_count()
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to update favorite status: {str(e)}")

    def update_favorites_count(self):
        """Update the count of favorite items in the sidebar"""
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM vault WHERE favorite = 1 AND deleted = 0")
                favorites_count = cursor.fetchone()[0]
                
                # Update the count in the second item (Favorites)
                favorites_item = self.main_items_list.item(1)
                if favorites_item:
                    item_widget = self.main_items_list.itemWidget(favorites_item)
                    if item_widget:
                        count_label = item_widget.layout().itemAt(2).widget()  # Get count label
                        count_label.setText(str(favorites_count))
                        
        except Exception as e:
            print(f"Error updating favorites count: {str(e)}")

    def update_password_details(self, password_data):
        """Update the right panel with password details"""
        if password_data:
            try:
                # Get favorite status from database
                with self.vault.conn:
                    cursor = self.vault.conn.cursor()
                    cursor.execute("""
                        SELECT favorite 
                        FROM vault 
                        WHERE title = ?
                    """, (password_data.get('title', ''),))
                    result = cursor.fetchone()
                    is_favorite = bool(result[0]) if result else False

                # Enable buttons
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.favorite_btn.setEnabled(True)
                self.toggle_password_btn.setEnabled(True)
                self.copy_password_btn.setEnabled(True)
                self.visit_website_btn.setEnabled(bool(password_data.get('website')))

                # Update favorite button state with database value
                self.favorite_btn.setChecked(is_favorite)
                self.favorite_btn.setText("⭐" if is_favorite else "☆")
                self.favorite_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        color: """ + ("#FFD700" if is_favorite else "#808080") + """;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #3C3C3C;
                    }
                    QPushButton:disabled {
                        color: #505050;
                    }
                """)

                # Update title and icon
                self.detail_title.setText(password_data.get('title', ''))
                if 'icon_data' in password_data and password_data['icon_data']:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(password_data['icon_data']):
                        self.detail_icon.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
                
                # Update form fields
                self.username_input.setText(password_data.get('username', ''))
                
                # Password is already decrypted by PasswordVault.get_entry()
                self.password_input.setText(password_data.get('password', ''))
                
                self.website_input.setText(password_data.get('website', ''))
                self.notes_input.setText(password_data.get('notes', ''))

                # Update category display
                category = password_data.get('category')
                if category:
                    self.category_label.setText(category)
                    # Ensure category exists in combo box
                    if self.categories_combo.findText(category) == -1:
                        self.categories_combo.addItem(category)
                else:
                    self.category_label.setText("No category selected")
                
                self.category_label.show()
                self.categories_combo.hide()
                
                # Update combo box selection
                index = self.categories_combo.findText(category) if category else 0
                self.categories_combo.setCurrentIndex(index)
                
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to update password details: {str(e)}")
                self.clear_right_panel()
        else:
            self.clear_right_panel()

    def toggle_password_visibility(self):
        """Toggle password field between visible and hidden"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("👁️")

    def toggle_edit_mode(self):
        """Toggle between edit and view modes"""
        try:
            if self.username_input.isReadOnly():  # Currently in view mode
                # Switch to edit mode
                self.edit_mode = True
                self.username_input.setReadOnly(False)
                self.password_input.setReadOnly(False)
                self.website_input.setReadOnly(False)
                self.notes_input.setReadOnly(False)
                
                # Disable favorite button during edit
                self.favorite_btn.setEnabled(False)
                
                # Show category combo box
                self.category_label.hide()
                self.categories_combo.show()
                
                # Store original values for cancel operation
                self.original_values = {
                    'username': self.username_input.text(),
                    'password': self.password_input.text(),
                    'website': self.website_input.text(),
                    'notes': self.notes_input.toPlainText(),
                    'category': self.category_label.text()
                }
                
                # Update buttons
                self.edit_btn.setText("💾 Save")
                self.delete_btn.setText("❌ Cancel")
                # Temporarily disconnect delete action and connect cancel action
                self.delete_btn.clicked.disconnect()
                self.delete_btn.clicked.connect(self.cancel_edit_mode)
                
            else:  # Currently in edit mode, save changes
                # Get the current values
                title = self.detail_title.text()
                username = self.username_input.text()
                password = self.password_input.text()
                website = self.website_input.text()
                notes = self.notes_input.toPlainText()
                category = self.categories_combo.currentText()
                
                # Validate required fields
                if not title or not username or not password:
                    show_message_box(self, QMessageBox.Icon.Warning, "Validation Error", 
                                      "Title, username, and password are required fields.")
                    return
                
                # Update the entry in the vault
                success = self.vault.update_entry(
                    title=title,
                    username=username,
                    password=password,
                    website=website,
                    notes=notes,
                    category=category,
                    master_password=self.master_password
                )
                
                if success:
                    # Reload the entries to reflect changes
                    self.load_vault_entries()
                    self.restore_view_mode()
                    show_message_box(self, QMessageBox.Icon.Information, "Success", "Changes saved successfully!")
                else:
                    show_message_box(self, QMessageBox.Icon.Critical, "Error", "Failed to save changes.")
                
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to toggle edit mode: {str(e)}")

    def cancel_edit_mode(self):
        """Cancel edit mode and restore original values"""
        try:
            # Restore original values
            self.username_input.setText(self.original_values['username'])
            self.password_input.setText(self.original_values['password'])
            self.website_input.setText(self.original_values['website'])
            self.notes_input.setText(self.original_values['notes'])
            self.category_label.setText(self.original_values['category'])
            
            # Restore view mode
            self.restore_view_mode()
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to cancel edit mode: {str(e)}")

    def restore_view_mode(self):
        """Restore view-only mode"""
        try:
            self.edit_mode = False
            self.username_input.setReadOnly(True)
            self.password_input.setReadOnly(True)
            self.website_input.setReadOnly(True)
            self.notes_input.setReadOnly(True)
            
            # Show category label
            self.categories_combo.hide()
            self.category_label.show()
            
            # Reset buttons
            self.edit_btn.setText("✏️ Edit")
            self.delete_btn.setText("🗑️ Delete")
            # Reconnect delete functionality
            self.delete_btn.clicked.disconnect()
            self.delete_btn.clicked.connect(self.delete_current_entry)
            self.favorite_btn.setEnabled(True)
            
        except Exception as e:
            print(f"Error restoring view mode: {str(e)}")

    def delete_current_entry(self):
        """Move the currently selected password entry to trash"""
        try:
            selected_item = self.password_list.currentItem()
            if not selected_item or not hasattr(selected_item, 'password_data'):
                return
            
            password_data = selected_item.password_data
            title = password_data['title']
            
            reply = QMessageBox.question(
                self, 'Move to Trash',
                'Are you sure you want to move this password entry to trash?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Move to trash in database
                with self.vault.conn:
                    cursor = self.vault.conn.cursor()
                    cursor.execute("UPDATE vault SET deleted = 1 WHERE title = ?", (title,))
                    self.vault.conn.commit()
                
                # Remove from list
                self.password_list.takeItem(self.password_list.row(selected_item))
                
                # Clear the form
                self.clear_right_panel()
                
                # Update counts
                self.update_total_count()  # Update All Items count
                self.update_favorites_count()  # Update Favorites count if applicable
                self.update_category_counts()  # Update category counts
                self.update_trash_count()  # Ensure trash count is updated
                
                show_message_box(self, QMessageBox.Icon.Information, "Success", "Password entry moved to trash!")
        
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to move entry to trash: {str(e)}")

    def update_trash_count(self):
        """Update the count of items in trash"""
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM vault WHERE deleted = 1")
                trash_count = cursor.fetchone()[0]
                
                # Update the count in Trash item (third item in the list)
                trash_item = self.main_items_list.item(2)
                if trash_item:
                    item_widget = self.main_items_list.itemWidget(trash_item)
                    if item_widget:
                        count_label = item_widget.layout().itemAt(2).widget()
                        count_label.setText(str(trash_count))
                    
        except Exception as e:
            print(f"Error updating trash count: {str(e)}")

    def setup_trash_panel(self):
        trash_panel = QWidget()
        trash_panel.setFixedWidth(400)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header section
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        header.setLayout(header_layout)
        
        # Icon and title
        trash_icon = QLabel("🗑️")
        trash_icon.setStyleSheet("font-size: 24px;")
        title_label = QLabel("Trash")
        title_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
        """)
        
        header_layout.addWidget(trash_icon)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Info section
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #808080;
                font-size: 14px;
            }
        """)
        info_layout = QVBoxLayout()
        info_widget.setLayout(info_layout)
        
        info_text = QLabel(
            "Items in the trash will be automatically deleted after 30 days. "
            "You can restore items or delete them permanently."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        # Details section
        details_widget = QWidget()
        details_widget.setStyleSheet("""
            QWidget {
                background-color: #2C2C2C;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        
        # Entry details (shown when item is selected)
        self.trash_title_label = QLabel()
        self.trash_username_label = QLabel()
        self.trash_date_label = QLabel()
        
        for label in [self.trash_title_label, self.trash_username_label, self.trash_date_label]:
            label.setStyleSheet("""
                color: white;
                font-size: 14px;
                padding: 5px 0;
            """)
            details_layout.addWidget(label)
        
        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_widget.setLayout(buttons_layout)
        
        restore_button = QPushButton("Restore")
        delete_button = QPushButton("Delete Permanently")
        
        button_style = """
            QPushButton {
                background-color: #3C3C3C;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4C4C4C;
            }
            QPushButton:pressed {
                background-color: #2C2C2C;
            }
        """
        
        restore_button.setStyleSheet(button_style)
        delete_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #8B0000;
            }
            QPushButton:hover {
                background-color: #A00000;
            }
        """)
        
        # Connect buttons to their respective slots
        restore_button.clicked.connect(self.restore_from_trash)
        delete_button.clicked.connect(self.permanently_delete_entry)
        
        buttons_layout.addWidget(restore_button)
        buttons_layout.addWidget(delete_button)
        
        # Add all sections to main layout
        layout.addWidget(header)
        layout.addWidget(info_widget)
        layout.addWidget(details_widget)
        layout.addStretch()
        layout.addWidget(buttons_widget)
        
        trash_panel.setLayout(layout)
        return trash_panel

    def update_trash_details(self, item):
        """Update the trash panel details when an item is selected"""
        if not item or not hasattr(item, 'password_data'):
            return
        
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    SELECT title, username, website 
                    FROM vault 
                    WHERE title = ? AND deleted = 1
                """, (item.password_data['title'],))
                result = cursor.fetchone()
                
                if result:
                    title, username, website = result
                    
                    # Update labels with more detailed information
                    self.trash_title_label.setText(f"🔑 {title}")
                    self.trash_title_label.setStyleSheet("""
                        color: white;
                        font-size: 18px;
                        font-weight: bold;
                        padding: 5px 0;
                    """)
                    
                    self.trash_username_label.setText(f"👤 Username: {username}")
                    self.trash_username_label.setStyleSheet("""
                        color: #CCCCCC;
                        font-size: 14px;
                        padding: 5px 0;
                    """)
                    
                    if website:
                        self.trash_date_label.setText(f"🌐 Website: {website}")
                    else:
                        self.trash_date_label.setText("🌐 No website specified")
                    self.trash_date_label.setStyleSheet("""
                        color: #CCCCCC;
                        font-size: 14px;
                        padding: 5px 0;
                    """)
                    
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to load trash details: {str(e)}")

    def on_trash_item_selected(self, item):
        if item:
            self.right_panel_2.show()  # Show the trash panel
            new_width = 600  # Adjust width as needed
            new_height = 500  # Adjust height as needed
            self.setMinimumSize(new_width, new_height)  # Set minimum size
            self.resize(new_width, new_height)  # Resize the window            

    def restore_from_trash(self):
        """Restore the selected password entry from trash"""
        current_item = self.password_list.currentItem()
        if not current_item or not hasattr(current_item, 'password_data'):
            return
            
        try:
            # Get the title from password data
            title = current_item.password_data['title']
            
            # Restore from trash in database
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("UPDATE vault SET deleted = 0 WHERE title = ?", (title,))
                self.vault.conn.commit()
            
            # Remove from list
            self.password_list.takeItem(self.password_list.row(current_item))
            
            # Clear the form
            self.clear_right_panel()
            
            # Update counts
            self.update_total_count()
            self.update_trash_count()
            
            show_message_box(self, QMessageBox.Icon.Information, "Success", "Password entry restored from trash!")
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to restore entry from trash: {str(e)}")

    def permanently_delete_entry(self):
        """Permanently delete the selected password entry from trash"""
        current_item = self.password_list.currentItem()
        if not current_item or not hasattr(current_item, 'password_data'):
            return
            
        reply = QMessageBox.warning(
            self, 'Permanent Deletion',
            'Are you sure you want to permanently delete this password entry?\nThis action cannot be undone!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get the title from password data
                title = current_item.password_data['title']
                
                # Delete from database
                if self.vault.delete_entry(title):
                    # Remove from list
                    self.password_list.takeItem(self.password_list.row(current_item))
                    
                    # Clear the form
                    self.clear_right_panel()
                    
                    # Update trash count
                    self.update_trash_count()
                    
                    show_message_box(self, QMessageBox.Icon.Information, "Success", "Password entry permanently deleted!")
                else:
                    show_message_box(self, QMessageBox.Icon.Warning, "Error", "Entry not found or already deleted.")
                    
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to delete entry: {str(e)}")

    def open_website(self):
        """Open website URL in default browser"""
        import webbrowser
        url = self.website_input.text().strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                webbrowser.open(url)
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Warning, "Error", f"Failed to open website: {str(e)}")

    def load_categories(self):
        """Load categories into the sidebar list"""
        try:
            self.categories_list.clear()
            self.categories_combo.clear()
            
            # Add "Create New Category" to combo
            self.categories_combo.addItem("➕ Create New Category")
            
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    SELECT category_names 
                    FROM categories 
                    ORDER BY category_names
                """)
                categories = cursor.fetchall()
                
                if categories:
                    self.categories_combo.insertSeparator(1)
                    for category in categories:
                        if category[0]:
                            # Simplified category data without color
                            category_data = {'name': category[0]}
                            # Add to sidebar list and combo box
                            self.add_category_to_list(category_data)
                            self.categories_combo.addItem(category[0])
                else:
                    # Only add "No Category" when there are no categories
                    self.categories_combo.insertSeparator(1)
                    self.categories_combo.addItem("No Category")
                    
                self.update_category_counts()
                    
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to load categories: {str(e)}")

    def clear_right_panel(self):
        """Clear all fields in the right panel"""
        try:
            # Clear all input fields
            self.detail_title.setText("")
            self.username_input.setText("")
            self.password_input.setText("")
            self.website_input.setText("")
            self.notes_input.setText("")
            self.category_label.setText("")
            self.categories_combo.setCurrentIndex(0)
            
            # Clear icon
            self.detail_icon.clear()
            self.detail_icon.setStyleSheet("QLabel { background-color: #2C2C2C; border-radius: 8px; }")
            
            # Disable all buttons
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.favorite_btn.setEnabled(False)
            self.toggle_password_btn.setEnabled(False)
            self.copy_password_btn.setEnabled(False)
            self.visit_website_btn.setEnabled(False)
            
            # Reset edit mode if active
            if not self.username_input.isReadOnly():
                self.restore_view_mode()
            
        except Exception as e:
            print(f"Error clearing right panel: {str(e)}")

    def on_sidebar_item_selected(self, item):
        """Handle sidebar item selection with filter toggling"""
        try:
            # Get the label text from the item widget
            item_widget = self.main_items_list.itemWidget(item) or self.categories_list.itemWidget(item)
            if not item_widget:
                return
            
            label = item_widget.layout().itemAt(0).widget()
            selected_text = label.text()
            
            # Store previous selection for comparison
            previous_filter = self.current_filter
            
            # Handle right panel state if visible
            if self.right_panel_1.isVisible() or self.right_panel_2.isVisible():
                if not self.username_input.isReadOnly():  # In edit mode
                    reply = QMessageBox.question(
                        self, 'Cancel Edit',
                        'You have unsaved changes. Do you want to cancel editing?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        # Restore previous selection
                        if previous_filter:
                            self.restore_previous_selection(previous_filter)
                        return
                
                # Hide both panels and clear contents
                self.right_panel_1.hide()
                self.right_panel_2.hide()
                self.clear_right_panel()
                self.reset_window_size()
            
            # Clear current password selection
            self.password_list.clearSelection()
            
            # Toggle filter if clicking the same item (except All Items)
            if selected_text == self.current_filter and selected_text != "🛡️ All Items":
                self.current_filter = None
                self.current_filter_type = None
                self.load_vault_entries()
                # Clear selections and select All Items
                self.main_items_list.clearSelection()
                self.categories_list.clearSelection()
                self.main_items_list.item(0).setSelected(True)
                return
            
            # Apply new filter
            self.current_filter = selected_text
            
            # Handle different filter types
            if selected_text == "🛡️ All Items":
                self.current_filter_type = None
                self.load_vault_entries()
                self.categories_list.clearSelection()
            elif selected_text == "⭐ Favorites":
                self.current_filter_type = "favorites"
                self.load_vault_entries(filter_type="favorites")
                self.categories_list.clearSelection()
            elif selected_text == "🗑️ Trash":
                self.current_filter_type = "trash"
                self.load_vault_entries(filter_type="trash")
                self.categories_list.clearSelection()
            else:
                # Category selection
                self.current_filter_type = "category"
                self.load_vault_entries(category=selected_text)
                self.main_items_list.clearSelection()
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to filter items: {str(e)}")

    def restore_previous_selection(self, previous_filter):
        """Restore the previous sidebar selection"""
        try:
            if previous_filter in ["🛡️ All Items", "⭐ Favorites", "🗑️ Trash"]:
                # Find and select the item in main_items_list
                for i in range(self.main_items_list.count()):
                    item = self.main_items_list.item(i)
                    item_widget = self.main_items_list.itemWidget(item)
                    if item_widget and item_widget.layout().itemAt(0).widget().text() == previous_filter:
                        self.main_items_list.setCurrentItem(item)
                        break
            else:
                # Find and select the item in categories_list
                for i in range(self.categories_list.count()):
                    item = self.categories_list.item(i)
                    item_widget = self.categories_list.itemWidget(item)
                    if item_widget and item_widget.layout().itemAt(0).widget().text() == previous_filter:
                        self.categories_list.setCurrentItem(item)
                        break
        except Exception as e:
            print(f"Error restoring previous selection: {str(e)}")

    def handle_category_selection(self, index):
        """Handle category combo box selection"""
        try:
            selected_text = self.categories_combo.currentText()
            
            if selected_text == "➕ Create New Category":
                # Store the previous index
                previous_index = max(0, self.categories_combo.currentIndex() - 1)
                
                # Show the add category dialog
                dialog = AddCategoryDialog(self.vault, self.master_password)
                result = dialog.exec()
                
                if result:
                    # Get the new category name and reload
                    new_category = dialog.get_values()['name']
                    self.load_categories()
                    
                    # Select the newly created category
                    index = self.categories_combo.findText(new_category)
                    if index >= 0:
                        self.categories_combo.setCurrentIndex(index)
                else:
                    # If cancelled, revert to previous selection
                    self.categories_combo.setCurrentIndex(previous_index)
                    
            # Force the combo box to reset its state
            self.categories_combo.setCurrentIndex(self.categories_combo.currentIndex())
                
        except Exception as e:
            print(f"Error handling category selection: {str(e)}")
            self.categories_combo.setCurrentIndex(0)

    def load_custom_fonts(self):
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'CourierPrime-Regular.ttf')
            if os.path.exists(font_path):
                QFontDatabase.addApplicationFont(font_path)
            else:
                print("Warning: Custom font file not found")
        except Exception as e:
            print(f"Error loading custom font: {str(e)}")
