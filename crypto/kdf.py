from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class KDFError(Exception):
    pass

def derive_room_key(password: str, salt: bytes, length: int = 32) -> bytes:
    if not isinstance(password, str):
        raise KDFError("Password must be a string")
    
    if not password:
        raise KDFError("Password cannot be empty")
    
    if not isinstance(salt, bytes):
        raise KDFError("Salt must be bytes")
    
    if len(salt) < 16:
        raise KDFError(f"Salt should be at least 16 bytes, got {len(salt)}")
    
    if length not in (16, 32, 64):
        raise KDFError(f"Key length must be 16, 32, or 64 bytes, got {length}")
    
    try:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=b"cmd-chat-room-key",
            backend=default_backend()
        )
        return hkdf.derive(password.encode('utf-8'))
    except Exception as e:
        raise KDFError(f"Key derivation failed: {e}")


def verify_derived_key(password: str, salt: bytes, expected_key: bytes, length: int = 32) -> bool:
    try:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=b"cmd-chat-room-key",
            backend=default_backend()
        )
        hkdf.verify(password.encode('utf-8'), expected_key)
        return True
    except Exception:
        return False