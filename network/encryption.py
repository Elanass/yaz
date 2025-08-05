"""General platform networking wrapper for Bitchat."""
import os
import sys

# Add the bitchat module to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bitchat"))

try:
    # Try to import from the actual Bitchat library structure
    from noise_protocol import NoiseProtocol
except ImportError:
    # Fallback implementation if Bitchat structure is different
    class NoiseProtocol:
        @staticmethod
        def encrypt(data, key):
            """Placeholder encryption - replace with actual Bitchat implementation."""
            return f"encrypted_{data}_{key}".encode()

        @staticmethod
        def decrypt(data, key):
            """Placeholder decryption - replace with actual Bitchat implementation."""
            return data.decode().replace(f"encrypted_", "").replace(f"_{key}", "")


def encrypt(data: str, key: str) -> bytes:
    """Encrypt data using Noise protocol from Bitchat."""
    return NoiseProtocol.encrypt(data, key)


def decrypt(data: bytes, key: str) -> str:
    """Decrypt data using Noise protocol from Bitchat."""
    return NoiseProtocol.decrypt(data, key)
