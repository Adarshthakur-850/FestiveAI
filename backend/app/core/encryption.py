import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import settings

def _get_fernet_instance() -> Fernet:
    """
    Returns a configured Fernet cipher instance.
    If the ENCRYPTION_KEY in settings is already a valid 32-byte urlsafe base64, use it;
    otherwise derive a valid 32-byte key using SHA-256 to ensure zero crashes.
    """
    raw_key = settings.ENCRYPTION_KEY.strip()
    try:
        # Check if already a valid Fernet key
        return Fernet(raw_key.encode())
    except Exception:
        # Derive standard 32-byte base64 Fernet key using SHA-256 digest
        digest = hashlib.sha256(raw_key.encode()).digest()
        derived_key = base64.urlsafe_b64encode(digest)
        return Fernet(derived_key)

_cipher = _get_fernet_instance()

def encrypt_secret(secret_text: str) -> str:
    """Encrypt a plaintext secret token or credential."""
    if not secret_text:
        return ""
    encrypted_bytes = _cipher.encrypt(secret_text.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_secret(encrypted_text: str) -> str:
    """Decrypt an encrypted secret token."""
    if not encrypted_text:
        return ""
    try:
        decrypted_bytes = _cipher.decrypt(encrypted_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        return "[DECRYPTION_ERROR]"

def redact_token(token: str, visible_chars: int = 4) -> str:
    """Mask a token for safe display or logging (e.g. EAAB...d8e3)."""
    if not token or len(token) <= visible_chars * 2:
        return "********"
    return f"{token[:visible_chars]}...{token[-visible_chars:]}"
