import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

def get_fernet_key() -> bytes:
    """
    Loads the Fernet encryption key from the ENCRYPTION_KEY environment variable.
    Raises an error if the key is not set or is invalid.
    The key must be a URL-safe base64-encoded 32-byte key.
    """
    key_str = os.getenv("ENCRYPTION_KEY")
    if not key_str:
        raise ValueError("ENCRYPTION_KEY environment variable not set. Please generate one using Fernet.generate_key().decode()")
    
    key_bytes = key_str.encode('utf-8')
    
    # Validate the key (optional but good practice)
    # A valid Fernet key is URL-safe base64 encoded and 32 bytes long.
    # The Fernet constructor itself will raise an error if the key is invalid.
    try:
        Fernet(key_bytes)
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY: {e}. Ensure it's a URL-safe base64-encoded 32-byte key.")
        
    return key_bytes

def encrypt_token(token: str, key: bytes) -> bytes:
    """
    Encrypts a string token using Fernet.
    """
    if not token:
        return None
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode('utf-8'))
    return encrypted_token

def decrypt_token(encrypted_token: bytes, key: bytes) -> str:
    """
    Decrypts an encrypted token using Fernet and returns it as a string.
    Returns None if the input is None.
    """
    if not encrypted_token:
        return None
    f = Fernet(key)
    decrypted_token_bytes = f.decrypt(encrypted_token)
    return decrypted_token_bytes.decode('utf-8')
