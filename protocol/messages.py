import json
from typing import Dict, Any

class MessageError(Exception):
    pass

def encode(msg: Dict[str, Any]) -> bytes:
    if not isinstance(msg, dict):
        raise MessageError("Message must be a dictionary")
    
    if "type" not in msg:
        raise MessageError("Message must have a 'type' field")
    
    try:
        json_str = json.dumps(msg, ensure_ascii=False)
        return (json_str + "\n").encode('utf-8')
    except (TypeError, ValueError) as e:
        raise MessageError(f"Failed to encode message: {e}")


def decode(line: bytes) -> Dict[str, Any]:
    if not isinstance(line, bytes):
        raise MessageError("Line must be bytes")
    
    if not line:
        raise MessageError("Cannot decode empty line")
    
    try:
        decoded_str = line.decode('utf-8').strip()
        msg = json.loads(decoded_str)
        
        if not isinstance(msg, dict):
            raise MessageError("Decoded message must be a dictionary")
        
        return msg
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise MessageError(f"Failed to decode message: {e}")


def create_auth_message(password: str) -> Dict[str, str]:
    return {"type": "auth", "password": password}

def create_init_message(room_salt: str) -> Dict[str, str]:
    return {"type": "init", "room_salt": room_salt}

def create_chat_message(user: str, encrypted_text: str) -> Dict[str, str]:
    return {"type": "message", "user": user, "text": encrypted_text}

def create_system_message(text: str) -> Dict[str, str]:
    return {"type": "system", "text": text}

def create_error_message(error_text: str) -> Dict[str, str]:
    return {"type": "error", "message": error_text}