"""
Encryption Service for Secure Data Storage

This service provides encryption and decryption functionality for sensitive medical data,
ensuring HIPAA/GDPR compliance with proper key management.
"""

import base64
import bcrypt
import json
from typing import Any, Dict, Union, Optional
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config.platform_config import config


class EncryptionService:
    """Service for encrypting and decrypting sensitive data with HIPAA compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._fernet = self._initialize_fernet()
        self.use_file_encryption = config.file_encryption_enabled
        self.patient_data_encryption = config.patient_data_encryption
    
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
                    iterations=480000  # HIPAA-compliant iteration count
                )
                key = base64.urlsafe_b64encode(kdf.derive(config.secret_key.encode()))
                
                # Log warning in non-production environments
                self.logger.warning(
                    "Generated temporary encryption key. "
                    "In production, set ENCRYPTION_KEY environment variable."
                )
                
                # Don't try to await in init method, use synchronous logging
                self.logger.warning(
                    "Temporary encryption key generated",
                    extra={"is_error": True, "environment": config.environment}
                )
            else:
                self.logger.error(
                    "Missing encryption key in production",
                    extra={"is_error": True, "environment": "production"}
                )
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
                    iterations=480000  # HIPAA-compliant iteration count
                )
                key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
            else:
                key = key.encode()
        
        if not key:
            self.logger.error("Missing encryption key", extra={"is_error": True})
            raise ValueError(
                "Encryption key not set. Set ENCRYPTION_KEY environment variable."
            )
            
        return Fernet(key)
    
    async def _log_encryption_event(self, message: str, is_error: bool = False, metadata: Optional[Dict[str, Any]] = None):
        """Log encryption events for audit trail"""
        try:
            # Import here to avoid circular import
            from services.event_logger.service import event_logger, EventCategory, EventSeverity
            
            severity = EventSeverity.ERROR if is_error else EventSeverity.INFO
            await event_logger.log_event(
                category=EventCategory.DATA_SECURITY,
                severity=severity,
                message=message,
                metadata=metadata or {}
            )
        except Exception as e:
            # Fallback to regular logging if event logger fails
            self.logger.error(f"Failed to log encryption event: {e}")
    
    async def encrypt_data(self, data: Union[str, bytes], data_type: str = "general") -> str:
        """
        Encrypt data using Fernet symmetric encryption with HIPAA compliance
        
        Args:
            data: The data to encrypt (string or bytes)
            data_type: The type of data being encrypted (for audit logging)
            
        Returns:
            Base64-encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Add metadata for auditing
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": data_type,
        }
        
        # Prepare data with metadata
        payload = {
            "metadata": metadata,
            "data": base64.b64encode(data).decode('utf-8')
        }
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        encrypted = self._fernet.encrypt(payload_bytes)
        
        # Log encryption event
        await self._log_encryption_event(
            f"Data encrypted: {data_type}",
            metadata={"data_type": data_type}
        )
        
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    async def decrypt_data(self, encrypted_data: Union[str, bytes], data_type: str = "general") -> str:
        """
        Decrypt Fernet-encrypted data with HIPAA compliance
        
        Args:
            encrypted_data: The encrypted data (base64-encoded string or bytes)
            data_type: The type of data being decrypted (for audit logging)
            
        Returns:
            Decrypted data as a string
        
        Raises:
            ValueError: If decryption fails
        """
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            decrypted = self._fernet.decrypt(encrypted_data)
            
            # Parse the payload
            payload = json.loads(decrypted.decode('utf-8'))
            original_data = base64.b64decode(payload["data"].encode('utf-8')).decode('utf-8')
            
            # Log decryption event
            await self._log_encryption_event(
                f"Data decrypted: {data_type}",
                metadata={
                    "data_type": data_type,
                    "timestamp": payload["metadata"]["timestamp"]
                }
            )
            
            return original_data
            
        except (InvalidToken, json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
            # Log decryption failure
            await self._log_encryption_event(
                f"Decryption failed: {str(e)}",
                is_error=True,
                metadata={"data_type": data_type, "error": str(e)}
            )
            
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """
        Create a secure password hash using bcrypt
        
        Args:
            password: The plaintext password
            
        Returns:
            Bcrypt hash string
        """
        # Use high work factor for HIPAA compliance
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=15)).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: The plaintext password to verify
            hashed_password: The stored bcrypt hash
            
        Returns:
            True if the password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    async def encrypt_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive patient data fields with HIPAA compliance
        
        Args:
            patient_data: Dictionary containing patient data
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        if not self.patient_data_encryption:
            return patient_data
        
        # Fields that should be encrypted for HIPAA compliance
        sensitive_fields = [
            "first_name", "last_name", "dob", "ssn", "address",
            "email", "phone", "medical_record_number"
        ]
        
        encrypted_data = patient_data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = await self.encrypt_data(
                    str(encrypted_data[field]), 
                    data_type=f"patient_{field}"
                )
        
        # Mark data as encrypted
        encrypted_data["_encrypted"] = True
        
        return encrypted_data
    
    async def decrypt_patient_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive patient data fields with HIPAA compliance
        
        Args:
            encrypted_data: Dictionary containing encrypted patient data
            
        Returns:
            Dictionary with sensitive fields decrypted
        """
        if not encrypted_data.get("_encrypted", False):
            return encrypted_data
        
        # Fields that should be decrypted
        sensitive_fields = [
            "first_name", "last_name", "dob", "ssn", "address",
            "email", "phone", "medical_record_number"
        ]
        
        decrypted_data = encrypted_data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = await self.decrypt_data(
                        decrypted_data[field],
                        data_type=f"patient_{field}"
                    )
                except ValueError:
                    # If decryption fails, leave as is
                    self.logger.warning(f"Failed to decrypt patient field: {field}")
        
        # Remove encryption marker
        decrypted_data.pop("_encrypted", None)
        
        return decrypted_data


# Create a singleton instance
encryption_service = EncryptionService()

# Helper functions for simpler usage in other modules
async def encrypt_sensitive_data(data, data_type="general"):
    """Helper function to encrypt data using the encryption service"""
    return await encryption_service.encrypt_data(data, data_type)

async def decrypt_sensitive_data(encrypted_data, data_type="general"):
    """Helper function to decrypt data using the encryption service"""
    return await encryption_service.decrypt_data(encrypted_data, data_type)

# Alias for compatibility with older code
encrypt_data = encrypt_sensitive_data
decrypt_data = decrypt_sensitive_data

def hash_password(password):
    """Helper function to hash passwords using the encryption service"""
    return encryption_service.hash_password(password)

def verify_password(password, hashed_password):
    """Helper function to verify passwords using the encryption service"""
    return encryption_service.verify_password(password, hashed_password)
