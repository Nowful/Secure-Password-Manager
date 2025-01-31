from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox,
                            QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon  # Add this import
from src.resources.styles import MAIN_STYLE, TITLE_STYLE # Import styles
import os
import re  # Add this import at the top
from argon2 import PasswordHasher  # Add this import
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet  # Add this import
import base64
from src.utils import resource_path, show_message_box


class  LoginDialog(QDialog):
    def __init__(self, vault):
        super().__init__()
        self.setWindowTitle("SPM Login")
        self.setModal(True)
        self.setFixedSize(275, 280)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMinimizeButtonHint)
        self.vault = vault
        self.master_password = None
        self.ph = PasswordHasher()
        self.eye_open_icon = QIcon(resource_path(os.path.join('resources', 'icons', 'eyeOpen_icon.png')))
        # self.eye_open_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'eyeOpen_icon.png'))
        # self.eye_closed_icon = QIcon(os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'eyeClose_icon.png'))
        self.eye_closed_icon = QIcon(resource_path(os.path.join('resources', 'icons', 'eyeClose_icon.png')))
        self.setStyleSheet(MAIN_STYLE)
        # self.master_key_file = os.path.join(os.path.dirname(__file__), '..', 'master.key')
        self.encryption_key = self.load_or_create_encryption_key()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)  # Reduce overall spacing between widgets
        
        # Add title
        title_label = QLabel("Secure Password Manager")
        title_label.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title_label)
        
        # Add some spacing after the title
        layout.addSpacing(15)  # Reduced from 20
        
        # Username section with reduced spacing
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white;")
        username_label.setContentsMargins(0, 0, 0, 0)  # Remove margins around label
        layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        layout.addSpacing(5)  # Small space between username and password sections
        
        # Password section with reduced spacing
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: white;")
        password_label.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(password_label)
        
        # Create horizontal layout for password input and toggle button
        password_layout = QHBoxLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        password_layout.addWidget(self.password_input)
        
        layout.addLayout(password_layout)
        layout.addSpacing(5)  # Small space between password and confirm password sections
        
        
        # Button layout
        button_layout = QHBoxLayout()
        
        if self.users_exist():
             # Update toggle confirm password visibility button
            self.toggle_password_button = QPushButton()
            self.toggle_password_button.setFixedSize(24, 24)
            self.toggle_password_button.setCheckable(True)
            self.toggle_password_button.setIcon(self.eye_closed_icon)  # Start with closed eye
            self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
            password_layout.addWidget(self.toggle_password_button)
            login_button = QPushButton("Login")
            login_button.clicked.connect(self.handle_login)
            button_layout.addWidget(login_button)
        else:
            # Confirm password section with reduced spacing
            self.confirm_password_label = QLabel("Confirm Password:")
            self.confirm_password_label.setStyleSheet("color: white;")
            self.confirm_password_label.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.confirm_password_label)
        
            # Create horizontal layout for confirm password input and toggle button
            confirm_password_layout = QHBoxLayout()
        
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm Password")
            confirm_password_layout.addWidget(self.confirm_password_input)
            # Update toggle confirm password visibility button
            self.toggle_confirm_password_button = QPushButton()
            self.toggle_confirm_password_button.setFixedSize(24, 24)
            self.toggle_confirm_password_button.setCheckable(True)
            self.toggle_confirm_password_button.setIcon(self.eye_closed_icon)  # Start with closed eye
            self.toggle_confirm_password_button.clicked.connect(self.toggle_confirm_password_visibility)
            confirm_password_layout.addWidget(self.toggle_confirm_password_button)
        
            layout.addLayout(confirm_password_layout)
        
            layout.addSpacing(10)  # Space before buttons
            signup_button = QPushButton("Sign Up")
            signup_button.clicked.connect(self.handle_signup)
            button_layout.addWidget(signup_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def users_exist(self):
        """Check if a master account exists in the database"""
        try:
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM master_account")
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to check master account: {str(e)}")
            return False

    def validate_password(self, password):
        """Validate password and show requirements if validation fails.""" 
        # Initialize validation message
        failed_conditions = []
        
        # Check length
        if not (12 <= len(password)):
            failed_conditions.append("Length must exceed 12 characters")
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            failed_conditions.append("Missing special character")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            failed_conditions.append("Missing uppercase letter")
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            failed_conditions.append("Missing lowercase letter")
        
        # Check for number
        if not re.search(r'[0-9]', password):
            failed_conditions.append("Missing number")
        
        # If any validation failed, show requirements
        if failed_conditions:
            requirements = f"""Your password doesn't meet the security requirements.

Your password must have:
• Minimum of 12 characters in length
• At least one special character (!@#$%^&*(),.?":{{}}|<>)
• At least one UPPERCASE letter
• At least one lowercase letter
• At least one number (0-9)

Current issues:
• {chr(10).join(failed_conditions)}

Example of a valid password: Secure2023!"""
            show_message_box(self, QMessageBox.Icon.Warning, "Password Requirements", requirements)
            return False
            
        return True

    def load_or_create_encryption_key(self):
        """Load existing encryption key or create a new one"""
        try:
            if (self.checkKeyExist()):
            # if os.path.exists('master.key'):
                with open('master.key', 'rb') as key_file:
                    return base64.urlsafe_b64decode(key_file.read())
            else:
                # Generate new key
                key = Fernet.generate_key()
                # os.makedirs(os.path.dirname('master.key'), exist_ok=True)
                with open('master.key', 'wb') as key_file:
                    key_file.write(base64.urlsafe_b64encode(key))
                return key
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to handle encryption key: {str(e)}")
            return None
    
    def checkKeyExist(self):
        try:
            if(open("master.key", "rb").read()):
                return True
        except:
            return False

    def handle_signup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not username or not password:
            show_message_box(self, QMessageBox.Icon.Warning, "Error", "Please enter both username and password")
            return
            
        if not self.validate_password(password):
            return
            
        if password != confirm_password:
            show_message_box(self, QMessageBox.Icon.Warning, "Error", "Passwords do not match!")
            return
            
        try:
            # Check if master account already exists
            if self.users_exist():
                show_message_box(self, QMessageBox.Icon.Warning, "Error", "Master account already exists!")
                return
            
            # Generate a salt - with error checking
            try:
                salt_bytes = os.urandom(16)
                salt = base64.urlsafe_b64encode(salt_bytes).decode('utf-8')
                if not salt:
                    raise ValueError("Salt generation failed")
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to generate salt: {str(e)}")
                return
            
            # Hash the password - with error checking
            try:
                if not password or not salt:
                    raise ValueError("Password or salt is empty")
                password_with_salt = password + salt
                master_password = self.ph.hash(password_with_salt)
                if not master_password:
                    raise ValueError("Password hashing failed")
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to hash password: {str(e)}")
                return
            
            # Store credentials in database
            try:
                with self.vault.conn:
                    cursor = self.vault.conn.cursor()
                    cursor.execute("""
                        INSERT INTO master_account (username, master_password, salt)
                        VALUES (?, ?, ?)
                    """, (username, master_password, salt))
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to store in database: {str(e)}")
                return
            
            # Initialize encryption
            try:
                self.master_password = password
            except Exception as e:
                show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to setup encryption: {str(e)}")
                return
            
            # After successful account creation
            self.confirm_password_input.setVisible(False)
            self.confirm_password_label.setVisible(False)
            
            show_message_box(self, QMessageBox.Icon.Information, "Success", "Master account created successfully!")
            self.accept()
            
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to create account: {str(e)}")

    def handle_login(self):
        # Get username and password
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            show_message_box(self, QMessageBox.Icon.Warning, "Error", "Please enter both username and password")
            return
            
        try:
            # Get user from database
            with self.vault.conn:
                cursor = self.vault.conn.cursor()
                cursor.execute("""
                    SELECT master_password, salt 
                    FROM master_account 
                    WHERE username = ?
                """, (username,))
                result = cursor.fetchone()
            
            if result:
                master_password, salt = result
                try:
                    self.ph.verify(master_password, password + salt)
                    self.master_password = password 
                    self.accept()
                    return
                except VerifyMismatchError:
                    show_message_box(self, QMessageBox.Icon.Warning, "Error", "Invalid password")
                    return
            else:
                show_message_box(self, QMessageBox.Icon.Warning, "Error", "User not found")
                
        except Exception as e:
            show_message_box(self, QMessageBox.Icon.Critical, "Error", f"Failed to handle login: {str(e)}")

    def toggle_password_visibility(self):
        """Toggle the password input's echo mode between Normal and Password"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setIcon(self.eye_open_icon)  # Show open eye when password is visible
            self.toggle_password_button.setChecked(True)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setIcon(self.eye_closed_icon)  # Show closed eye when password is hidden
            self.toggle_password_button.setChecked(False)

    def toggle_confirm_password_visibility(self):
        """Toggle the confirm password input's echo mode between Normal and Password"""
        if self.confirm_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_confirm_password_button.setIcon(self.eye_open_icon)  # Show open eye when password is visible
            self.toggle_confirm_password_button.setChecked(True)
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_confirm_password_button.setIcon(self.eye_closed_icon)  # Show closed eye when password is hidden
            self.toggle_confirm_password_button.setChecked(False)