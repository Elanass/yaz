"""
IPFS Client Service for Immutable Evidence Storage

This service provides a secure interface to store and retrieve medical data in IPFS,
ensuring immutable evidence storage with proper encryption and access control.
"""

import os
import json
import asyncio
import base64
import httpx
from typing import Any, Dict, List, Optional, Union

from core.config.settings import get_feature_config
from core.services.base import BaseService
from core.utils.helpers import HashUtils
from core.services.encryption import EncryptionService


class IPFSClient(BaseService):
    """IPFS client for storing and retrieving medical evidence"""
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("ipfs")
        self.encryption = EncryptionService()
        self.base_url = self.config.get("ipfs_api_url", "http://localhost:5001/api/v0")
        self.gateway_url = self.config.get("ipfs_gateway_url", "http://localhost:8080/ipfs")
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def add_json(self, data: Dict[str, Any], encrypt: bool = True) -> str:
        """
        Add JSON data to IPFS with optional encryption
        
        Args:
            data: The JSON data to store
            encrypt: Whether to encrypt the data before storage
            
        Returns:
            The IPFS hash (CID) of the stored data
        """
        # Add audit metadata
        data["_metadata"] = {
            "timestamp": self.get_current_timestamp(),
            "schema_version": "1.0",
            "hash": HashUtils.hash_dict(data)
        }
        
        # Encrypt if required
        content = data
        if encrypt:
            content = self.encryption.encrypt_data(json.dumps(data))
        
        # Convert to JSON string if still a dict
        if isinstance(content, dict):
            content = json.dumps(content)
            
        # Add to IPFS
        files = {'file': content}
        response = await self.http_client.post(f"{self.base_url}/add", files=files)
        
        if response.status_code != 200:
            self.logger.error(f"Failed to add to IPFS: {response.text}")
            raise Exception(f"IPFS add failed: {response.status_code}")
            
        result = response.json()
        return result.get("Hash")
    
    async def get_json(self, ipfs_hash: str, decrypt: bool = True) -> Dict[str, Any]:
        """
        Get JSON data from IPFS with optional decryption
        
        Args:
            ipfs_hash: The IPFS hash (CID) to retrieve
            decrypt: Whether to decrypt the data after retrieval
            
        Returns:
            The retrieved data as a dictionary
        """
        response = await self.http_client.post(f"{self.base_url}/cat?arg={ipfs_hash}")
        
        if response.status_code != 200:
            self.logger.error(f"Failed to get from IPFS: {response.text}")
            raise Exception(f"IPFS get failed: {response.status_code}")
        
        content = response.text
        
        # Decrypt if required
        if decrypt:
            try:
                content = self.encryption.decrypt_data(content)
            except Exception as e:
                self.logger.error(f"Failed to decrypt IPFS data: {str(e)}")
                raise Exception(f"Decryption failed: {str(e)}")
        
        # Parse JSON
        try:
            if isinstance(content, str):
                return json.loads(content)
            return content
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse IPFS data as JSON")
            raise Exception("Invalid JSON format")
    
    async def pin_hash(self, ipfs_hash: str) -> bool:
        """
        Pin a hash to ensure it's not garbage collected
        
        Args:
            ipfs_hash: The IPFS hash (CID) to pin
            
        Returns:
            True if successful, False otherwise
        """
        response = await self.http_client.post(f"{self.base_url}/pin/add?arg={ipfs_hash}")
        return response.status_code == 200
    
    def get_gateway_url(self, ipfs_hash: str) -> str:
        """
        Get the public gateway URL for a hash
        
        Args:
            ipfs_hash: The IPFS hash (CID)
            
        Returns:
            The public gateway URL
        """
        return f"{self.gateway_url}/{ipfs_hash}"
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()
