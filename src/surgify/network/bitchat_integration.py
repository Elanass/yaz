"""Surgify-specific networking implementation using Bitchat."""
import json
import logging
import os
# Import from the root network module
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from network import (decrypt, encrypt, fetch_and_merge, queue_message, receive,
                     send)

logger = logging.getLogger(__name__)


class SurgifyMessageHandler:
    """Surgify-specific message handling for medical communications."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.encryption_key = (
            f"surgify_{node_id}_key"  # In production, use proper key management
        )

    def send_medical_data(self, destination: str, data: Dict[str, Any]) -> bool:
        """Send encrypted medical data to another Surgify node."""
        try:
            # Add Surgify-specific metadata
            surgify_message = {
                "type": "medical_data",
                "from": self.node_id,
                "to": destination,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "protocol_version": "1.0",
            }

            # Serialize and encrypt
            message_json = json.dumps(surgify_message)
            encrypted_data = encrypt(message_json, self.encryption_key)

            # Send via mesh network
            success = send(destination, encrypted_data)

            if not success:
                # Queue for offline sync if send fails
                queue_message(
                    {
                        "destination": destination,
                        "encrypted_data": encrypted_data.hex(),
                        "message_type": "medical_data",
                    }
                )
                logger.info(f"Message to {destination} queued for offline sync")

            return success

        except Exception as e:
            logger.error(f"Failed to send medical data: {e}")
            return False

    def send_case_consultation(
        self, destination: str, case_id: str, consultation_data: Dict[str, Any]
    ) -> bool:
        """Send case consultation request to another medical professional."""
        consultation_message = {
            "type": "case_consultation",
            "case_id": case_id,
            "consultation_data": consultation_data,
            "urgency": consultation_data.get("urgency", "normal"),
        }

        return self.send_medical_data(destination, consultation_message)

    def receive_messages(self) -> List[Dict[str, Any]]:
        """Receive and decrypt incoming messages."""
        try:
            encrypted_messages = receive()
            decrypted_messages = []

            for encrypted_msg in encrypted_messages:
                try:
                    decrypted_json = decrypt(encrypted_msg, self.encryption_key)
                    message = json.loads(decrypted_json)

                    # Validate Surgify message format
                    if self._is_valid_surgify_message(message):
                        decrypted_messages.append(message)
                    else:
                        logger.warning("Received invalid Surgify message format")

                except Exception as e:
                    logger.error(f"Failed to decrypt message: {e}")

            return decrypted_messages

        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")
            return []

    def sync_offline_messages(self) -> List[Dict[str, Any]]:
        """Sync offline messages and attempt to resend."""
        try:
            offline_messages = fetch_and_merge()
            resent_messages = []

            for msg in offline_messages:
                if msg.get("message_type") == "medical_data":
                    # Attempt to resend
                    encrypted_data = bytes.fromhex(msg["encrypted_data"])
                    success = send(msg["destination"], encrypted_data)

                    if success:
                        msg["status"] = "resent_successfully"
                        logger.info(
                            f"Successfully resent message to {msg['destination']}"
                        )
                    else:
                        msg["status"] = "resend_failed"
                        # Re-queue for another attempt
                        queue_message(msg)

                    resent_messages.append(msg)

            return resent_messages

        except Exception as e:
            logger.error(f"Failed to sync offline messages: {e}")
            return []

    def _is_valid_surgify_message(self, message: Dict[str, Any]) -> bool:
        """Validate that the message follows Surgify protocol."""
        required_fields = [
            "type",
            "from",
            "to",
            "timestamp",
            "data",
            "protocol_version",
        ]
        return all(field in message for field in required_fields)


# Global Surgify message handler instance
surgify_handler: Optional[SurgifyMessageHandler] = None


def initialize_surgify_network(node_id: str) -> SurgifyMessageHandler:
    """Initialize Surgify networking with a specific node ID."""
    global surgify_handler
    surgify_handler = SurgifyMessageHandler(node_id)
    logger.info(f"Initialized Surgify network for node: {node_id}")
    return surgify_handler


def get_surgify_handler() -> Optional[SurgifyMessageHandler]:
    """Get the current Surgify message handler."""
    return surgify_handler
