from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import logging

class Encryption:
    # Add constants
    PBKDF2_ITERATIONS = 310000
    SALT_LENGTH = 16
    KEY_LENGTH = 32
    NONCE_LENGTH = 12

    def __init__(self, master_password: str, salt: bytes = None):
        # Allow salt to be passed in or generate new one
        self.salt = salt if salt is not None else os.urandom(16)
        # Increase iterations for better security
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=310000,
            backend=default_backend()
        )
        self.key = kdf.derive(master_password.encode())
        self.master_password = master_password

    # Add method to get salt
    def get_salt(self) -> bytes:
        return self.salt

    def encrypt(self, data: str) -> bytes:
        # Generate a random nonce
        nonce = os.urandom(12)
        # Create ChaCha20-Poly1305 cipher
        chacha = ChaCha20Poly1305(self.key)
        # Encrypt the data
        encrypted_data = chacha.encrypt(
            nonce,
            data.encode(),
            None
        )
        # Combine salt + nonce + encrypted data
        return base64.b64encode(self.salt + nonce + encrypted_data)

    def decrypt(self, encrypted_data: bytes) -> str:
        try:
            if encrypted_data is None:
                return ""
                
            # Decode the data
            raw_data = base64.b64decode(encrypted_data)
            
            # Verify minimum data length
            min_length = self.SALT_LENGTH + self.NONCE_LENGTH
            if len(raw_data) < min_length:
                logging.error(f"Encrypted data too short: {len(raw_data)} bytes")
                raise ValueError("Encrypted data is too short")
            
            # Split salt, nonce and ciphertext
            salt = raw_data[:16]
            nonce = raw_data[16:28]
            ciphertext = raw_data[28:]
            
            # Use the salt from the encrypted data to derive the key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=310000,
                backend=default_backend()
            )
            key = kdf.derive(self.master_password.encode())
            
            # Create cipher with derived key
            chacha = ChaCha20Poly1305(key)
            
            # Decrypt the data
            decrypted_data = chacha.decrypt(
                nonce,
                ciphertext,
                None
            )
            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Decryption failed: {str(e)}")
            raise ValueError("Failed to decrypt data") from e