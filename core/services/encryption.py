"""
Encryption Service for Secure Data Storage

This service provides encryption and decryption functionality for sensitive medical data,
ensuring HIPAA/GDPR compliance with proper key management.
"""

import os
import base64
import bcrypt
from typing import Any, Dict, Union
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config.platform_config import config


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._fernet = self._initialize_fernet()
    
    def _initialize_fernet(self) -> Fernet:
        """Initialize the Fernet encryption with the configured key"""
        key = config.encryption_key
        
        # If no key is set, generate one (dev environments only)
        if not key or key == "dev-encryption-key-32-chars-long":
            if config.environment != "production":
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000
                )
                key = base64.urlsafe_b64encode(kdf.derive(config.secret_key.encode()))
                
                # Log warning in non-production environments
                self.logger.warning(
                    "Generated temporary encryption key. "
                    "In production, set ENCRYPTION_KEY environment variable."
                )
            else:
                raise ValueError(
                    "Encryption key not set for production. Set ENCRYPTION_KEY environment variable."
                )
        
        # Ensure key is properly formatted for Fernet
        if isinstance(key, str):
            if len(key) != 44:  # Fernet key length in base64
                # Derive proper key from provided key
                salt = b'gastric_adci_salt'  # Static salt for consistent key derivation
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000
                )
                key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
            else:
                key = key.encode()
        
        if not key:
            raise ValueError(
                "Encryption key not set. Set ENCRYPTION_KEY environment variable."
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
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data (placeholder implementation)."""
        return f"encrypted({data})"

    def decrypt_sensitive_data(self, data: str) -> str:
        """Decrypt sensitive data (placeholder implementation)."""
        return data.replace("encrypted(", "").rstrip(")")


# Singleton instance
encryption_service = EncryptionService()
