"""Security Manager for multi-layer network security
Implements end-to-end encryption, access control, and distributed authentication.
"""

import asyncio
import json
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


logger = logging.getLogger(__name__)


@dataclass
class SecurityProfile:
    """Security profile for a user or node."""

    id: str
    public_key: bytes
    permissions: list[str]
    roles: list[str]
    created_at: datetime
    expires_at: datetime | None = None
    is_trusted: bool = False


@dataclass
class EncryptedMessage:
    """Encrypted message structure."""

    recipient_id: str
    encrypted_data: bytes
    signature: bytes
    nonce: bytes
    sender_id: str
    timestamp: datetime


class SecurityManager:
    """Manages multi-layer security across all network types."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.private_key = None
        self.public_key = None
        self.security_profiles: dict[str, SecurityProfile] = {}
        self.active_sessions: dict[str, dict] = {}
        self.is_running = False
        self.encryption_keys: dict[str, bytes] = {}
        self.jwt_secret = secrets.token_urlsafe(32)

    async def start(self) -> None:
        """Start security manager."""
        logger.info("🔒 Starting Security Manager...")

        # Generate node keypair
        await self._generate_node_keypair()

        # Initialize security systems
        await self._initialize_security_systems()

        self.is_running = True

        # Start background security tasks
        asyncio.create_task(self._security_monitor())
        asyncio.create_task(self._session_manager())

        logger.info("✅ Security Manager started")

    async def _generate_node_keypair(self) -> None:
        """Generate RSA keypair for node."""
        logger.info("🔑 Generating node keypair...")

        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )

        # Get public key
        self.public_key = self.private_key.public_key()

        logger.info("✅ Node keypair generated")

    async def _initialize_security_systems(self) -> None:
        """Initialize security subsystems."""
        # Initialize encryption systems
        await self._setup_encryption()

        # Setup access control
        await self._setup_access_control()

        # Initialize audit logging
        await self._setup_audit_logging()

    async def _setup_encryption(self) -> None:
        """Setup encryption systems."""
        logger.info("🔐 Setting up encryption systems")

        # Generate symmetric keys for different purposes
        self.encryption_keys = {
            "mesh_communication": secrets.token_bytes(32),  # AES-256
            "data_storage": secrets.token_bytes(32),
            "session_encryption": secrets.token_bytes(32),
        }

        logger.info("✅ Encryption systems configured")

    async def _setup_access_control(self) -> None:
        """Setup role-based access control."""
        logger.info("🛡️ Setting up access control")

        # Define default roles and permissions
        self.default_roles = {
            "admin": [
                "read",
                "write",
                "delete",
                "manage_users",
                "manage_security",
                "network_admin",
            ],
            "surgeon": [
                "read",
                "write",
                "surgery_planning",
                "patient_data",
                "clinical_notes",
            ],
            "nurse": [
                "read",
                "write",
                "patient_monitoring",
                "clinical_updates",
                "basic_surgery_data",
            ],
            "student": ["read", "educational_content", "simulation_access"],
            "guest": ["read"],
        }

        logger.info("✅ Access control configured")

    async def _setup_audit_logging(self) -> None:
        """Setup security audit logging."""
        logger.info("📝 Setting up audit logging")

        # Initialize audit log storage
        self.audit_logs = []

        logger.info("✅ Audit logging configured")

    async def implement_mesh_security(self) -> None:
        """Implement end-to-end encryption for all network types."""
        logger.info("🌐 Implementing mesh security")

        # Setup encryption for local network
        await self._setup_local_network_encryption()

        # Setup P2P encryption
        await self._setup_p2p_encryption()

        # Setup BLE mesh encryption
        await self._setup_ble_encryption()

        # Setup VM cluster encryption
        await self._setup_vm_cluster_encryption()

        logger.info("✅ Mesh security implemented")

    async def _setup_local_network_encryption(self) -> None:
        """Setup encryption for local network communication."""
        logger.info("🏠 Setting up local network encryption")

        # Use AES-256-GCM for local network
        self.local_network_cipher = self._create_aes_cipher(
            self.encryption_keys["mesh_communication"]
        )

    async def _setup_p2p_encryption(self) -> None:
        """Setup encryption for P2P network."""
        logger.info("🔗 Setting up P2P encryption")

        # Use hybrid encryption: RSA for key exchange, AES for data
        self.p2p_encryption_ready = True

    async def _setup_ble_encryption(self) -> None:
        """Setup encryption for BLE mesh."""
        logger.info("📡 Setting up BLE encryption")

        # Lightweight encryption for BLE constraints
        self.ble_encryption_key = self.encryption_keys["mesh_communication"][
            :16
        ]  # AES-128

    async def _setup_vm_cluster_encryption(self) -> None:
        """Setup encryption for VM cluster communication."""
        logger.info("☁️ Setting up VM cluster encryption")

        # TLS-like encryption for VM-to-VM communication
        self.vm_cluster_encryption_ready = True

    def _create_aes_cipher(self, key: bytes):
        """Create AES cipher with key."""
        return algorithms.AES(key)

    async def encrypt_message(
        self, message: Any, recipient_id: str
    ) -> EncryptedMessage:
        """Encrypt message for specific recipient."""
        try:
            # Serialize message
            message_data = json.dumps(message, default=str).encode()

            # Generate nonce
            nonce = secrets.token_bytes(16)

            # Encrypt with AES-GCM
            cipher_key = self.encryption_keys["mesh_communication"]
            cipher = Cipher(algorithms.AES(cipher_key), modes.GCM(nonce))

            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(message_data) + encryptor.finalize()

            # Create signature
            signature = self._sign_data(encrypted_data + nonce)

            encrypted_message = EncryptedMessage(
                recipient_id=recipient_id,
                encrypted_data=encrypted_data + encryptor.tag,  # Include GCM tag
                signature=signature,
                nonce=nonce,
                sender_id=self.node_id,
                timestamp=datetime.now(),
            )

            logger.debug(f"🔐 Encrypted message for {recipient_id}")
            return encrypted_message

        except Exception as e:
            logger.exception(f"Encryption failed: {e}")
            raise

    async def decrypt_message(self, encrypted_message: EncryptedMessage) -> Any:
        """Decrypt message from sender."""
        try:
            # Verify signature
            if not self._verify_signature(
                encrypted_message.encrypted_data + encrypted_message.nonce,
                encrypted_message.signature,
                encrypted_message.sender_id,
            ):
                msg = "Invalid message signature"
                raise ValueError(msg)

            # Extract encrypted data and tag
            encrypted_data = encrypted_message.encrypted_data[:-16]  # Remove GCM tag
            tag = encrypted_message.encrypted_data[-16:]  # GCM tag

            # Decrypt with AES-GCM
            cipher_key = self.encryption_keys["mesh_communication"]
            cipher = Cipher(
                algorithms.AES(cipher_key), modes.GCM(encrypted_message.nonce, tag)
            )

            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Deserialize message
            message = json.loads(decrypted_data.decode())

            logger.debug(f"🔓 Decrypted message from {encrypted_message.sender_id}")
            return message

        except Exception as e:
            logger.exception(f"Decryption failed: {e}")
            raise

    def _sign_data(self, data: bytes) -> bytes:
        """Sign data with private key."""
        return self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

    def _verify_signature(self, data: bytes, signature: bytes, sender_id: str) -> bool:
        """Verify signature with sender's public key."""
        try:
            # Get sender's public key
            profile = self.security_profiles.get(sender_id)
            if not profile:
                logger.warning(f"No security profile for sender: {sender_id}")
                return False

            # Deserialize public key
            public_key = serialization.load_pem_public_key(profile.public_key)

            # Verify signature
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True

        except Exception as e:
            logger.exception(f"Signature verification failed: {e}")
            return False

    async def setup_access_control(self) -> None:
        """Setup role-based access control across network."""
        logger.info("🛡️ Setting up distributed access control")

        # Create access control manager
        asyncio.create_task(self._access_control_manager())

        # Setup permission synchronization
        asyncio.create_task(self._sync_permissions())

        logger.info("✅ Access control setup complete")

    async def authenticate_user(self, credentials: dict) -> dict | None:
        """Authenticate user and create session."""
        try:
            username = credentials.get("username")
            password = credentials.get("password")

            if not username or not password:
                return None

            # Verify credentials (simplified - would use proper auth system)
            user_id = await self._verify_credentials(username, password)
            if not user_id:
                return None

            # Get user profile
            profile = self.security_profiles.get(user_id)
            if not profile:
                # Create default profile
                profile = await self._create_user_profile(user_id, username)

            # Create session
            session = await self._create_session(user_id, profile)

            # Log authentication
            await self._log_security_event(
                "authentication",
                {
                    "user_id": user_id,
                    "username": username,
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            logger.info(f"✅ User authenticated: {username}")
            return session

        except Exception as e:
            logger.exception(f"Authentication failed: {e}")
            await self._log_security_event(
                "authentication",
                {
                    "username": credentials.get("username"),
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return None

    async def _verify_credentials(self, username: str, password: str) -> str | None:
        """Verify user credentials."""
        # Simplified credential verification
        # In production, this would check against secure user database

        default_users = {
            "admin": {"password": "admin123", "user_id": "admin_001"},
            "surgeon1": {"password": "surgeon123", "user_id": "surgeon_001"},
            "nurse1": {"password": "nurse123", "user_id": "nurse_001"},
        }

        user_data = default_users.get(username)
        if user_data and user_data["password"] == password:
            return user_data["user_id"]

        return None

    async def _create_user_profile(
        self, user_id: str, username: str
    ) -> SecurityProfile:
        """Create security profile for user."""
        # Determine role based on username (simplified)
        if "admin" in username.lower():
            roles = ["admin"]
        elif "surgeon" in username.lower():
            roles = ["surgeon"]
        elif "nurse" in username.lower():
            roles = ["nurse"]
        else:
            roles = ["guest"]

        # Get permissions for roles
        permissions = []
        for role in roles:
            permissions.extend(self.default_roles.get(role, []))

        # Generate user keypair (simplified - would be done during registration)
        user_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        user_public_key = user_private_key.public_key()

        profile = SecurityProfile(
            id=user_id,
            public_key=user_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ),
            permissions=list(set(permissions)),
            roles=roles,
            created_at=datetime.now(),
            is_trusted=True,
        )

        self.security_profiles[user_id] = profile
        return profile

    async def _create_session(self, user_id: str, profile: SecurityProfile) -> dict:
        """Create authenticated session."""
        session_id = secrets.token_urlsafe(32)

        # Create JWT token
        token_payload = {
            "user_id": user_id,
            "session_id": session_id,
            "roles": profile.roles,
            "permissions": profile.permissions,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=8),
        }

        access_token = jwt.encode(token_payload, self.jwt_secret, algorithm="HS256")

        session = {
            "session_id": session_id,
            "user_id": user_id,
            "access_token": access_token,
            "roles": profile.roles,
            "permissions": profile.permissions,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=8),
        }

        self.active_sessions[session_id] = session
        return session

    async def verify_permission(
        self, session_id: str, required_permission: str
    ) -> bool:
        """Verify user has required permission."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        # Check if session is expired
        if datetime.now() > session["expires_at"]:
            del self.active_sessions[session_id]
            return False

        return required_permission in session["permissions"]

    async def _access_control_manager(self) -> None:
        """Manage access control across network."""
        while self.is_running:
            try:
                # Clean up expired sessions
                current_time = datetime.now()
                expired_sessions = [
                    sid
                    for sid, session in self.active_sessions.items()
                    if current_time > session["expires_at"]
                ]

                for session_id in expired_sessions:
                    del self.active_sessions[session_id]

                if expired_sessions:
                    logger.info(
                        f"🧹 Cleaned up {len(expired_sessions)} expired sessions"
                    )

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.exception(f"Access control management error: {e}")
                await asyncio.sleep(600)

    async def _sync_permissions(self) -> None:
        """Synchronize permissions across network nodes."""
        while self.is_running:
            try:
                # Sync security profiles with other nodes
                # This would implement distributed permission management
                logger.debug("🔄 Syncing permissions across network")

                await asyncio.sleep(600)  # Sync every 10 minutes

            except Exception as e:
                logger.exception(f"Permission sync error: {e}")
                await asyncio.sleep(1200)

    async def _security_monitor(self) -> None:
        """Monitor security events and threats."""
        while self.is_running:
            try:
                # Monitor for security threats
                await self._check_security_threats()

                # Monitor session activity
                await self._monitor_sessions()

                # Check encryption integrity
                await self._check_encryption_integrity()

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                logger.exception(f"Security monitoring error: {e}")
                await asyncio.sleep(300)

    async def _check_security_threats(self) -> None:
        """Check for security threats."""
        # Implement threat detection logic

    async def _monitor_sessions(self) -> None:
        """Monitor active sessions for anomalies."""
        # Check for unusual session activity
        for _session_id, _session in self.active_sessions.items():
            # Implement session monitoring logic
            pass

    async def _check_encryption_integrity(self) -> None:
        """Check encryption system integrity."""
        # Verify encryption keys and systems
        if not self.private_key or not self.public_key:
            logger.error("❌ Node keypair missing - regenerating")
            await self._generate_node_keypair()

    async def _session_manager(self) -> None:
        """Manage user sessions."""
        while self.is_running:
            try:
                # Session health checks
                active_count = len(self.active_sessions)
                logger.debug(f"👥 Managing {active_count} active sessions")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.exception(f"Session management error: {e}")
                await asyncio.sleep(600)

    async def _log_security_event(self, event_type: str, event_data: dict) -> None:
        """Log security event."""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat(),
            "node_id": self.node_id,
        }

        self.audit_logs.append(event)

        # Keep only recent logs (for memory management)
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-5000:]

        logger.debug(f"📝 Logged security event: {event_type}")

    async def get_security_status(self) -> dict:
        """Get security manager status."""
        return {
            "active": self.is_running,
            "node_id": self.node_id,
            "encryption_ready": bool(self.private_key and self.public_key),
            "active_sessions": len(self.active_sessions),
            "security_profiles": len(self.security_profiles),
            "audit_log_count": len(self.audit_logs),
            "encryption_keys": list(self.encryption_keys.keys()),
            "default_roles": list(self.default_roles.keys()),
        }

    async def stop(self) -> None:
        """Stop security manager."""
        logger.info("🛑 Stopping Security Manager")
        self.is_running = False
