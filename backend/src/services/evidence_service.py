"""
Tamper-proof Evidence Storage Service
IPFS-based immutable evidence logging with cryptographic verification
"""

import json
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiofiles
import ipfshttpclient
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import structlog

from ..core.config import settings
from ..db.models import EvidenceLog, User
from ..schemas.evidence import EvidenceType, EvidenceMetadata
from sqlalchemy.orm import Session

logger = structlog.get_logger(__name__)

@dataclass
class EvidenceRecord:
    """Structured evidence record"""
    evidence_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    content: Union[str, bytes, Dict]
    metadata: EvidenceMetadata
    source: str
    created_by: Optional[int]
    tags: List[str]
    clinical_context: Dict[str, Any]
    
    def __post_init__(self):
        if not self.evidence_id:
            self.evidence_id = self._generate_evidence_id()
    
    def _generate_evidence_id(self) -> str:
        """Generate unique evidence ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.sha256(str(self.content).encode()).hexdigest()[:8]
        return f"EVD_{timestamp}_{content_hash}"

class IPFSStorageService:
    """IPFS-based immutable storage service"""
    
    def __init__(self, ipfs_endpoint: str = "/ip4/127.0.0.1/tcp/5001"):
        self.ipfs_endpoint = ipfs_endpoint
        self._client = None
        
    async def get_client(self):
        """Get IPFS client with connection pooling"""
        if not self._client:
            try:
                self._client = ipfshttpclient.connect(self.ipfs_endpoint)
                # Test connection
                await self._client.id()
                logger.info("Connected to IPFS", endpoint=self.ipfs_endpoint)
            except Exception as e:
                logger.error("Failed to connect to IPFS", error=str(e))
                raise
        return self._client
    
    async def store_content(self, content: Union[str, bytes, Dict]) -> str:
        """Store content in IPFS and return hash"""
        client = await self.get_client()
        
        try:
            if isinstance(content, dict):
                content = json.dumps(content, sort_keys=True)
            elif isinstance(content, str):
                content = content.encode('utf-8')
            
            # Add to IPFS
            result = client.add_bytes(content)
            ipfs_hash = result['Hash']
            
            logger.info("Content stored in IPFS", hash=ipfs_hash, size=len(content))
            return ipfs_hash
            
        except Exception as e:
            logger.error("Failed to store content in IPFS", error=str(e))
            raise
    
    async def retrieve_content(self, ipfs_hash: str) -> bytes:
        """Retrieve content from IPFS"""
        client = await self.get_client()
        
        try:
            content = client.cat(ipfs_hash)
            logger.info("Content retrieved from IPFS", hash=ipfs_hash)
            return content
            
        except Exception as e:
            logger.error("Failed to retrieve content from IPFS", hash=ipfs_hash, error=str(e))
            raise
    
    async def pin_content(self, ipfs_hash: str) -> bool:
        """Pin content to prevent garbage collection"""
        client = await self.get_client()
        
        try:
            client.pin.add(ipfs_hash)
            logger.info("Content pinned in IPFS", hash=ipfs_hash)
            return True
            
        except Exception as e:
            logger.error("Failed to pin content in IPFS", hash=ipfs_hash, error=str(e))
            return False

class CryptographicVerification:
    """Cryptographic verification service for evidence integrity"""
    
    def __init__(self, private_key_path: str = None):
        self.private_key_path = private_key_path or settings.EVIDENCE_PRIVATE_KEY_PATH
        self._private_key = None
        self._public_key = None
    
    async def _load_keys(self):
        """Load or generate cryptographic keys"""
        if self._private_key:
            return
            
        try:
            # Try to load existing private key
            if Path(self.private_key_path).exists():
                async with aiofiles.open(self.private_key_path, 'rb') as f:
                    private_key_data = await f.read()
                    self._private_key = load_pem_private_key(
                        private_key_data, 
                        password=None
                    )
            else:
                # Generate new key pair
                self._private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                # Save private key
                private_key_pem = self._private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                Path(self.private_key_path).parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(self.private_key_path, 'wb') as f:
                    await f.write(private_key_pem)
                    
            self._public_key = self._private_key.public_key()
            logger.info("Cryptographic keys loaded/generated")
            
        except Exception as e:
            logger.error("Failed to load/generate keys", error=str(e))
            raise
    
    async def sign_evidence(self, evidence_data: bytes) -> str:
        """Digitally sign evidence data"""
        await self._load_keys()
        
        try:
            signature = self._private_key.sign(
                evidence_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            signature_hex = signature.hex()
            logger.info("Evidence signed", signature_length=len(signature))
            return signature_hex
            
        except Exception as e:
            logger.error("Failed to sign evidence", error=str(e))
            raise
    
    async def verify_signature(self, evidence_data: bytes, signature_hex: str) -> bool:
        """Verify digital signature"""
        await self._load_keys()
        
        try:
            signature = bytes.fromhex(signature_hex)
            
            self._public_key.verify(
                signature,
                evidence_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.info("Signature verified successfully")
            return True
            
        except Exception as e:
            logger.warning("Signature verification failed", error=str(e))
            return False
    
    def create_content_hash(self, content: Union[str, bytes, Dict]) -> str:
        """Create SHA-256 hash of content"""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        elif isinstance(content, str):
            content = content.encode('utf-8')
        
        return hashlib.sha256(content).hexdigest()

class TamperProofEvidenceService:
    """Comprehensive tamper-proof evidence service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ipfs_service = IPFSStorageService()
        self.crypto_service = CryptographicVerification()
        
    async def store_evidence(
        self,
        evidence: EvidenceRecord,
        file_content: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Store evidence with full tamper-proof guarantees"""
        
        try:
            # 1. Create structured evidence package
            evidence_package = {
                "evidence_id": evidence.evidence_id,
                "evidence_type": evidence.evidence_type.value,
                "title": evidence.title,
                "description": evidence.description,
                "content": evidence.content if not file_content else "FILE_ATTACHMENT",
                "metadata": asdict(evidence.metadata),
                "source": evidence.source,
                "created_by": evidence.created_by,
                "tags": evidence.tags,
                "clinical_context": evidence.clinical_context,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            # 2. Create content hash
            content_hash = self.crypto_service.create_content_hash(evidence_package)
            evidence_package["content_hash"] = content_hash
            
            # 3. Store main evidence in IPFS
            main_content = json.dumps(evidence_package, sort_keys=True)
            main_ipfs_hash = await self.ipfs_service.store_content(main_content)
            
            # 4. Store file attachment if present
            file_ipfs_hash = None
            if file_content:
                file_ipfs_hash = await self.ipfs_service.store_content(file_content)
                evidence_package["file_ipfs_hash"] = file_ipfs_hash
                # Update hash with file reference
                updated_content = json.dumps(evidence_package, sort_keys=True)
                main_ipfs_hash = await self.ipfs_service.store_content(updated_content)
            
            # 5. Create digital signature
            signature = await self.crypto_service.sign_evidence(main_content.encode())
            
            # 6. Pin content in IPFS
            await self.ipfs_service.pin_content(main_ipfs_hash)
            if file_ipfs_hash:
                await self.ipfs_service.pin_content(file_ipfs_hash)
            
            # 7. Store evidence log in database
            evidence_log = EvidenceLog(
                evidence_id=evidence.evidence_id,
                evidence_type=evidence.evidence_type.value,
                title=evidence.title,
                description=evidence.description,
                content_hash=content_hash,
                ipfs_hash=main_ipfs_hash,
                file_ipfs_hash=file_ipfs_hash,
                digital_signature=signature,
                metadata=asdict(evidence.metadata),
                source=evidence.source,
                created_by=evidence.created_by,
                tags=evidence.tags,
                clinical_context=evidence.clinical_context,
                verification_status="verified",
                blockchain_tx_hash=None  # Optional blockchain integration
            )
            
            self.db.add(evidence_log)
            self.db.commit()
            
            logger.info(
                "Evidence stored successfully",
                evidence_id=evidence.evidence_id,
                ipfs_hash=main_ipfs_hash,
                content_hash=content_hash
            )
            
            return {
                "evidence_id": evidence.evidence_id,
                "ipfs_hash": main_ipfs_hash,
                "file_ipfs_hash": file_ipfs_hash,
                "content_hash": content_hash,
                "digital_signature": signature,
                "timestamp": datetime.utcnow().isoformat(),
                "verification_status": "verified"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to store evidence", error=str(e))
            raise
    
    async def retrieve_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Retrieve and verify evidence integrity"""
        
        try:
            # 1. Get evidence log from database
            evidence_log = self.db.query(EvidenceLog).filter(
                EvidenceLog.evidence_id == evidence_id
            ).first()
            
            if not evidence_log:
                raise ValueError(f"Evidence not found: {evidence_id}")
            
            # 2. Retrieve content from IPFS
            evidence_content = await self.ipfs_service.retrieve_content(
                evidence_log.ipfs_hash
            )
            
            # 3. Verify digital signature
            signature_valid = await self.crypto_service.verify_signature(
                evidence_content, 
                evidence_log.digital_signature
            )
            
            # 4. Verify content hash
            current_hash = self.crypto_service.create_content_hash(evidence_content)
            hash_valid = current_hash == evidence_log.content_hash
            
            # 5. Parse evidence content
            evidence_data = json.loads(evidence_content.decode('utf-8'))
            
            # 6. Retrieve file if present
            file_content = None
            if evidence_log.file_ipfs_hash:
                file_content = await self.ipfs_service.retrieve_content(
                    evidence_log.file_ipfs_hash
                )
            
            logger.info(
                "Evidence retrieved",
                evidence_id=evidence_id,
                signature_valid=signature_valid,
                hash_valid=hash_valid
            )
            
            return {
                "evidence_data": evidence_data,
                "file_content": file_content,
                "verification": {
                    "signature_valid": signature_valid,
                    "hash_valid": hash_valid,
                    "ipfs_hash": evidence_log.ipfs_hash,
                    "content_hash": evidence_log.content_hash,
                    "timestamp": evidence_log.created_at.isoformat()
                },
                "metadata": evidence_log.metadata
            }
            
        except Exception as e:
            logger.error("Failed to retrieve evidence", evidence_id=evidence_id, error=str(e))
            raise
    
    async def verify_evidence_chain(
        self, 
        evidence_ids: List[str]
    ) -> Dict[str, Any]:
        """Verify integrity of multiple evidence records"""
        
        verification_results = []
        overall_valid = True
        
        for evidence_id in evidence_ids:
            try:
                result = await self.retrieve_evidence(evidence_id)
                verification = result["verification"]
                
                is_valid = verification["signature_valid"] and verification["hash_valid"]
                overall_valid = overall_valid and is_valid
                
                verification_results.append({
                    "evidence_id": evidence_id,
                    "is_valid": is_valid,
                    "signature_valid": verification["signature_valid"],
                    "hash_valid": verification["hash_valid"],
                    "ipfs_hash": verification["ipfs_hash"]
                })
                
            except Exception as e:
                verification_results.append({
                    "evidence_id": evidence_id,
                    "is_valid": False,
                    "error": str(e)
                })
                overall_valid = False
        
        return {
            "overall_valid": overall_valid,
            "total_evidence": len(evidence_ids),
            "valid_count": sum(1 for r in verification_results if r.get("is_valid", False)),
            "verification_results": verification_results,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
    
    async def search_evidence(
        self,
        query: str,
        evidence_type: Optional[EvidenceType] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Search evidence with advanced filtering"""
        
        from sqlalchemy import and_, or_
        
        query_filter = self.db.query(EvidenceLog)
        
        # Apply filters
        if evidence_type:
            query_filter = query_filter.filter(EvidenceLog.evidence_type == evidence_type.value)
        
        if tags:
            query_filter = query_filter.filter(EvidenceLog.tags.overlap(tags))
        
        if created_by:
            query_filter = query_filter.filter(EvidenceLog.created_by == created_by)
        
        if start_date:
            query_filter = query_filter.filter(EvidenceLog.created_at >= start_date)
        
        if end_date:
            query_filter = query_filter.filter(EvidenceLog.created_at <= end_date)
        
        # Text search in title and description
        if query:
            query_filter = query_filter.filter(
                or_(
                    EvidenceLog.title.ilike(f"%{query}%"),
                    EvidenceLog.description.ilike(f"%{query}%")
                )
            )
        
        # Get total count
        total = query_filter.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        evidence_logs = query_filter.offset(offset).limit(per_page).all()
        
        return {
            "evidence": [
                {
                    "evidence_id": log.evidence_id,
                    "evidence_type": log.evidence_type,
                    "title": log.title,
                    "description": log.description,
                    "source": log.source,
                    "tags": log.tags,
                    "created_at": log.created_at.isoformat(),
                    "verification_status": log.verification_status,
                    "ipfs_hash": log.ipfs_hash,
                    "has_file": bool(log.file_ipfs_hash)
                }
                for log in evidence_logs
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
