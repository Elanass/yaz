"""
Simplified Encryption Service for Surgify Platform
"""

import base64
import logging
import os
from typing import Any, Dict, Optional, Union

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ...core.config.unified_config import get_settings


class EncryptionService:
    """Simple encryption service for sensitive data"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self._fernet = self._initialize_fernet()

    def _initialize_fernet(self) -> Fernet:
        """Initialize the Fernet encryption with the configured key"""
        try:
            # Use the secret key from settings to derive encryption key
            password = self.settings.secret_key.encode()
            salt = b"surgify_salt_123"  # Use a fixed salt for simplicity

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return Fernet(key)

        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to a generated key
            return Fernet(Fernet.generate_key())

    def encrypt_data(self, data: Union[str, Dict[str, Any]]) -> str:
        """Encrypt data and return base64 encoded string"""
        try:
            if isinstance(data, dict):
                data = str(data)

            encrypted_bytes = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()

        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return data  # Return original data if encryption fails

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()

        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Return original data if decryption fails


# Global service instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get the global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
