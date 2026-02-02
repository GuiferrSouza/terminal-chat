from cryptography.fernet import Fernet, InvalidToken
import base64

class EncryptionError(Exception):
    pass

def fernet_from_key(key: bytes) -> Fernet:
    if not isinstance(key, bytes):
        raise EncryptionError("Key must be bytes")
    
    if len(key) != 32:
        raise EncryptionError(f"Key must be 32 bytes, got {len(key)}")
    
    try:
        url_safe_key = base64.urlsafe_b64encode(key)
        return Fernet(url_safe_key)
    except Exception as e:
        raise EncryptionError(f"Failed to create Fernet instance: {e}")


def encrypt(fernet: Fernet, text: str) -> str:
    if not isinstance(text, str):
        raise EncryptionError("Text must be a string")
    
    try:
        encrypted_bytes = fernet.encrypt(text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        raise EncryptionError(f"Encryption failed: {e}")


def decrypt(fernet: Fernet, token: str) -> str:
    if not isinstance(token, str):
        raise EncryptionError("Token must be a string")
    
    try:
        decrypted_bytes = fernet.decrypt(token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        raise EncryptionError("Invalid or corrupted token")
    except Exception as e:
        raise EncryptionError(f"Decryption failed: {e}")