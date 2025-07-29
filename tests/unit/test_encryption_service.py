"""
Unit tests for the Encryption Service
Verifies HIPAA-compliant functionality and security
"""

import pytest
import os
import base64
import json
from unittest.mock import patch, AsyncMock

from core.services.encryption import EncryptionService
from services.event_logger.service import EventCategory, EventSeverity

# Test data
SAMPLE_PASSWORD = "TestP@ssw0rd123!"
SAMPLE_PATIENT_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1970-01-01",
    "ssn": "123-45-6789",
    "address": "123 Main St, Anytown, USA",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "medical_record_number": "MRN12345",
    "diagnosis": "Gastric Cancer",
    "tumor_stage": "T2N0M0"
}


@pytest.fixture
def mock_event_logger():
    """Mock the event logger for testing"""
    with patch('services.event_logger.service.event_logger') as mock:
        mock.log_event = AsyncMock()
        yield mock


@pytest.fixture
def encryption_service():
    """Create an encryption service for testing"""
    # Set a fixed encryption key for testing
    os.environ["ENCRYPTION_KEY"] = "dGVzdGtleWZvcmZlcm5ldHRlc3RpbmdhbmRub3RoaW5nZWxzZQ=="
    
    # Create the service
    service = EncryptionService()
    return service


@pytest.mark.asyncio
async def test_encrypt_decrypt_data(encryption_service, mock_event_logger):
    """Test basic encryption and decryption"""
    # Test data
    test_data = "This is sensitive medical data"
    
    # Encrypt the data
    encrypted = await encryption_service.encrypt_data(test_data, "test")
    
    # Verify it's encrypted (not equal to original)
    assert encrypted != test_data
    assert isinstance(encrypted, str)
    
    # Decrypt the data
    decrypted = await encryption_service.decrypt_data(encrypted, "test")
    
    # Verify decryption works
    assert decrypted == test_data
    
    # Verify events were logged
    mock_event_logger.log_event.assert_called()
    assert mock_event_logger.log_event.call_count >= 2


@pytest.mark.asyncio
async def test_encrypt_decrypt_with_metadata(encryption_service):
    """Test that encrypted data includes metadata"""
    # Test data
    test_data = "PHI data with metadata"
    
    # Encrypt the data
    encrypted = await encryption_service.encrypt_data(test_data, "phi")
    
    # Decode and decrypt manually to check structure
    encrypted_bytes = base64.urlsafe_b64decode(encrypted.encode('utf-8'))
    decrypted_bytes = encryption_service._fernet.decrypt(encrypted_bytes)
    payload = json.loads(decrypted_bytes.decode('utf-8'))
    
    # Verify metadata exists
    assert "metadata" in payload
    assert "timestamp" in payload["metadata"]
    assert payload["metadata"]["type"] == "phi"
    
    # Verify data is correctly stored
    original_data = base64.b64decode(payload["data"].encode('utf-8')).decode('utf-8')
    assert original_data == test_data


@pytest.mark.asyncio
async def test_decrypt_invalid_data(encryption_service, mock_event_logger):
    """Test error handling for invalid encrypted data"""
    # Invalid data
    invalid_data = "ThisIsNotValidEncryptedData"
    
    # Attempt to decrypt should raise ValueError
    with pytest.raises(ValueError):
        await encryption_service.decrypt_data(invalid_data, "test")
    
    # Verify error was logged
    mock_event_logger.log_event.assert_called_with(
        category=EventCategory.DATA_SECURITY,
        severity=EventSeverity.ERROR,
        message="Decryption failed: Padding is incorrect.",
        metadata={'data_type': 'test', 'error': 'Padding is incorrect.'}
    )


def test_password_hashing(encryption_service):
    """Test secure password hashing and verification"""
    # Hash the password
    hashed = encryption_service.hash_password(SAMPLE_PASSWORD)
    
    # Verify it's not the original password
    assert hashed != SAMPLE_PASSWORD
    
    # Verify correct password matches
    assert encryption_service.verify_password(SAMPLE_PASSWORD, hashed)
    
    # Verify incorrect password fails
    assert not encryption_service.verify_password("WrongPassword", hashed)


@pytest.mark.asyncio
async def test_patient_data_encryption(encryption_service):
    """Test encryption of patient data with HIPAA compliance"""
    # Enable patient data encryption
    encryption_service.patient_data_encryption = True
    
    # Encrypt patient data
    encrypted_patient = await encryption_service.encrypt_patient_data(SAMPLE_PATIENT_DATA)
    
    # Verify sensitive fields are encrypted
    sensitive_fields = [
        "first_name", "last_name", "dob", "ssn", "address",
        "email", "phone", "medical_record_number"
    ]
    
    for field in sensitive_fields:
        assert encrypted_patient[field] != SAMPLE_PATIENT_DATA[field]
    
    # Verify non-sensitive fields are unchanged
    assert encrypted_patient["diagnosis"] == SAMPLE_PATIENT_DATA["diagnosis"]
    assert encrypted_patient["tumor_stage"] == SAMPLE_PATIENT_DATA["tumor_stage"]
    
    # Verify encryption marker is set
    assert encrypted_patient["_encrypted"] is True
    
    # Decrypt and verify
    decrypted_patient = await encryption_service.decrypt_patient_data(encrypted_patient)
    
    # Verify all original data is restored
    for key, value in SAMPLE_PATIENT_DATA.items():
        assert decrypted_patient[key] == value
    
    # Verify encryption marker is removed
    assert "_encrypted" not in decrypted_patient


@pytest.mark.asyncio
async def test_encryption_disabled(encryption_service):
    """Test behavior when encryption is disabled"""
    # Disable patient data encryption
    encryption_service.patient_data_encryption = False
    
    # Process patient data
    processed_patient = await encryption_service.encrypt_patient_data(SAMPLE_PATIENT_DATA)
    
    # Verify data is unchanged
    assert processed_patient == SAMPLE_PATIENT_DATA
