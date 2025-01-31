import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import os

class PasswordVault:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.connect() 
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Debug - Database connected: {bool(self.conn)}")
        except Exception as e:
            print(f"Debug - Database connection error: {str(e)}")
            raise
            
    def __enter__(self):
        """Context manager entry"""
        if not self.conn:
            self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_database(self):
        """Create database tables if they don't exist"""
        if self.conn:
            self.conn.close()
        
        self.connect()  # Use the existing connect method
        if not self.conn:
            raise Exception("Failed to establish database connection")
            
        if self.conn is None:
            raise Exception("Database connection is not established.")

        if self.conn is None:
            raise Exception("Database connection is not established.")

        cursor = self.conn.cursor()
        
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS master_account (
                username TEXT PRIMARY KEY,
                master_password TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT,
                encrypted_password BLOB NOT NULL,
                salt BLOB,
                website TEXT,
                icon BLOB,
                notes TEXT,
                category TEXT,
                favorite BOOLEAN DEFAULT 0,
                deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_names TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

           
        ''')
        self.conn.commit()

    def setup_encryption(self, master_password: str):
        """Initialize encryption with master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt',  
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.cipher = Fernet(key)

    def add_entry(self, table: str, **kwargs):
        """
        Dynamically insert data into a specified table.

        Parameters:
            table (str): Name of the table to insert data into.
            **kwargs: Column-value pairs for the insertion.
        """
        if not self.conn:
            self.connect()
        if not self.conn:
            raise Exception("Database connection failed")

        # Ensure encryption is initialized if a sensitive field (e.g., password) is present
        if "password" in kwargs:
            if not hasattr(self, 'cipher') or not self.cipher:
                raise Exception("Encryption not initialized. Please login first.")
            try:
                kwargs["encrypted_password"] = self.cipher.encrypt(kwargs.pop("password").encode())
            except Exception as e:
                raise Exception(f"Encryption failed: {str(e)}. Please ensure proper login.")

        # Construct the query dynamically
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())

        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'

        # Execute the query
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, values)
            self.conn.commit()
        except Exception as e:
            raise Exception(f"Database insertion failed: {str(e)}")


    def get_entry(self, table: str, **conditions):
        """
        Dynamically retrieve entry from specified table based on conditions
        
        Args:
            table (str): Name of the table to query
            **conditions: Key-value pairs for WHERE clause
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        
        # Get column names for the table
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query
        query = f'SELECT {", ".join(columns)} FROM {table}'
        values = tuple()
        
        # Add WHERE clause only if conditions exist
        if conditions:
            where_clause = ' AND '.join(f'{key} = ?' for key in conditions.keys())
            query += f' WHERE {where_clause}'
            values = tuple(conditions.values())
        
        cursor.execute(query, values)
        entry = cursor.fetchone()
        
        if entry:
            # Create dict with column names as keys
            result = dict(zip(columns, entry))
            
            # Decrypt password if it exists and cipher is initialized
            if 'encrypted_password' in result and hasattr(self, 'cipher'):
                try:
                    result['password'] = self.cipher.decrypt(result['encrypted_password']).decode()
                    del result['encrypted_password']
                except Exception as e:
                    raise Exception(f"Failed to decrypt password: {str(e)}")
                
            return result
            
        return None

    def create_master_account(self, username: str, master_password: str) -> bool:
        """Create the master account for first-time setup"""
        if self.conn is None:
            raise Exception("Database connection is not established.")

        if self.conn is None:
            raise Exception("Database connection is not established.")

        cursor = self.conn.cursor()
        
        # Check if master account already exists
        cursor.execute('SELECT COUNT(*) FROM master_account')
        if cursor.fetchone()[0] > 0:
            return False
        
        # Generate salt and hash password
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(master_password, salt)
        
        # Store master account
        cursor.execute('''
            INSERT INTO master_account (username, password_hash, salt)
            VALUES (?, ?, ?)
        ''', (username, password_hash, salt))
        self.conn.commit()
        
        # Setup encryption with master password
        self.setup_encryption(master_password)
        return True

    def login(self, username: str, master_password: str) -> bool:
        """Verify login credentials and setup encryption"""
        if self.conn is None:
            raise Exception("Database connection is not established.")

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT password_hash, salt 
            FROM master_account 
            WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        if not result:
            return False
        
        stored_hash, salt = result
        password_hash = self._hash_password(master_password, salt)
        
        if password_hash == stored_hash:
            # Make sure encryption is set up when login is successful
            self.setup_encryption(master_password)
            return True
        return False

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256(
            password.encode() + bytes.fromhex(salt)
        ).hexdigest()

    def verify_master_password(self, input_password: str) -> bool:
        """Verify the input password against the stored master password"""
        if self.conn is None:
            raise Exception("Database connection is not established.")

        if self.conn is None:
            raise Exception("Database connection is not established.")

        cursor = self.conn.cursor()
        cursor.execute('SELECT password_hash, salt FROM master_account')
        result = cursor.fetchone()

        if not result:
            return False

        stored_hash, salt = result
        input_hash = self._hash_password(input_password, salt)

        return input_hash == stored_hash

    def delete_entry(self, title: str):
        """Delete password entry by title"""
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM vault WHERE title = ?', (title,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Failed to delete entry: {str(e)}")

    def update_entry(self, title: str, username: str, password: str, website: str = None, 
                    notes: str = None, category: str = None, master_password: str = None) -> bool:
        """
        Update an existing entry in the vault
        
        Args:
            title (str): Title of the entry to update
            username (str): Updated username
            password (str): Updated password
            website (str, optional): Updated website URL
            notes (str, optional): Updated notes
            category (str, optional): Updated category
            master_password (str): Master password for encryption
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if not self.conn:
                self.connect()
            
            if not hasattr(self, 'cipher'):
                self.setup_encryption(master_password)
            
            # Encrypt the new password
            encrypted_password = self.cipher.encrypt(password.encode())
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE vault 
                SET username = ?, 
                    encrypted_password = ?,
                    website = ?,
                    notes = ?,
                    category = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE title = ?
            ''', (username, encrypted_password, website, notes, category, title))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating entry: {str(e)}")
            return False