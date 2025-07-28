"""
Encryption Service for Secure Data Storage

This service provides encryption and decryption functionality for sensitive medical data,
ensuring HIPAA/GDPR compliance with proper key management.
"""

import os
import base64
from typing import Any, Dict, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config.settings import get_security_config
from core.services.base import BaseService


class EncryptionService(BaseService):
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        super().__init__()
        self.config = get_security_config()
        self._fernet = self._initialize_fernet()
    
    def _initialize_fernet(self) -> Fernet:
        """Initialize the Fernet encryption with the configured key"""
        key = self.config.get("encryption_key")
        
        # If no key is set, generate one (dev environments only)
        if not key and os.getenv("ENVIRONMENT") != "production":
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.config.get("secret_key").encode()))
            
            # Log warning in non-production environments
            if os.getenv("ENVIRONMENT") != "production":
                self.logger.warning(
                    "Generated temporary encryption key. "
                    "In production, set SECURITY_ENCRYPTION_KEY environment variable."
                )
        
        if not key:
            raise ValueError(
                "Encryption key not set. Set SECURITY_ENCRYPTION_KEY environment variable."
            )
            
        return Fernet(key)
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using Fernet symmetric encryption
        
        Args:
            data: The data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        encrypted = self._fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: Union[str, bytes]) -> str:
        """
        Decrypt Fernet-encrypted data
        
        Args:
            encrypted_data: The encrypted data (base64-encoded string or bytes)
            
        Returns:
            Decrypted data as a string
        """
        if isinstance(encrypted_data, str):
            encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            
        decrypted = self._fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def hash_password(self, password: str) -> str:
        """
        Create a secure hash of a password
        
        Args:
            password: The password to hash
            
        Returns:
            Securely hashed password
        """
        import bcrypt
        
        # Generate a salt and hash the password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: The password to verify
            hashed_password: The stored hash to check against
            
        Returns:
            True if the password matches, False otherwise
        """
        import bcrypt
        
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
