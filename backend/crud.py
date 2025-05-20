from sqlalchemy.orm import Session
import json # For handling scopes_g list
from .database import User, SessionLocal
from .encryption import encrypt_token, decrypt_token, get_fernet_key
from google.oauth2.credentials import Credentials # For constructing Credentials object

# Helper to get a DB session, similar to what might be used in a FastAPI dependency
def get_db_session() -> Session:
    """
    Creates and returns a new SQLAlchemy session.
    Ensure this session is closed by the caller, typically using a try/finally block
    or a FastAPI dependency pattern.
    """
    return SessionLocal()

def create_or_update_user(
    db: Session, 
    google_id: str, 
    access_token: str, 
    refresh_token: str = None,
    token_uri: str = None,
    client_id_g: str = None,
    client_secret_g: str = None,
    scopes_g: list[str] = None
) -> User:
    """
    Creates a new user or updates an existing user's YouTube tokens and other credential details.
    Sensitive information is encrypted before storing.
    """
    key = get_fernet_key()
    
    encrypted_access_token = encrypt_token(access_token, key) if access_token else None
    encrypted_refresh_token = encrypt_token(refresh_token, key) if refresh_token else None
    encrypted_client_id_g = encrypt_token(client_id_g, key) if client_id_g else None
    encrypted_client_secret_g = encrypt_token(client_secret_g, key) if client_secret_g else None
    
    encrypted_scopes_g = None
    if scopes_g:
        try:
            scopes_json_string = json.dumps(scopes_g)
            encrypted_scopes_g = encrypt_token(scopes_json_string, key)
        except TypeError as e:
            # Handle error if scopes_g is not JSON serializable, though list of strings should be.
            print(f"Error serializing scopes_g to JSON: {e}") 
            # Decide on error handling: raise error, log, or skip storing scopes
            pass 
    
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if user:
        user.encrypted_youtube_access_token = encrypted_access_token
        user.encrypted_youtube_refresh_token = encrypted_refresh_token
        user.token_uri = token_uri
        user.client_id_g = encrypted_client_id_g
        user.client_secret_g = encrypted_client_secret_g
        user.scopes_g = encrypted_scopes_g
    else:
        user = User(
            google_id=google_id,
            encrypted_youtube_access_token=encrypted_access_token,
            encrypted_youtube_refresh_token=encrypted_refresh_token,
            token_uri=token_uri,
            client_id_g=encrypted_client_id_g,
            client_secret_g=encrypted_client_secret_g,
            scopes_g=encrypted_scopes_g
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user

def get_user_by_google_id(db: Session, google_id: str) -> User | None:
    """
    Queries and returns a user by their Google ID.
    The tokens in the returned User object will still be encrypted.
    Returns None if the user is not found.
    """
    return db.query(User).filter(User.google_id == google_id).first()

def get_full_credentials_for_user(db: Session, google_id: str) -> Credentials | None:
    """
    Retrieves user from DB, decrypts their stored credentials, and returns a 
    google.oauth2.credentials.Credentials object.
    Returns None if user not found or essential credentials are missing.
    """
    user = get_user_by_google_id(db, google_id)
    if not user:
        return None

    key = get_fernet_key()

    decrypted_access_token = decrypt_token(user.encrypted_youtube_access_token, key) if user.encrypted_youtube_access_token else None
    decrypted_refresh_token = decrypt_token(user.encrypted_youtube_refresh_token, key) if user.encrypted_youtube_refresh_token else None
    decrypted_client_id = decrypt_token(user.client_id_g, key) if user.client_id_g else None
    decrypted_client_secret = decrypt_token(user.client_secret_g, key) if user.client_secret_g else None
    scopes_list_str = decrypt_token(user.scopes_g, key) if user.scopes_g else None
    
    decrypted_scopes = None
    if scopes_list_str:
        try:
            decrypted_scopes = json.loads(scopes_list_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding scopes JSON for user {google_id}: {e}")
            # Decide on error handling: return None, raise error, or proceed without scopes
            pass # Proceeding without scopes for now if they are corrupted

    # Essential check: access token is required to form valid Credentials
    if not decrypted_access_token:
        print(f"User {google_id} is missing a decrypted access token. Cannot form Credentials object.")
        return None
    
    # token_uri and client_id are also usually required for refresh.
    # client_secret is needed if the client type requires it.
    if not user.token_uri or not decrypted_client_id:
         print(f"User {google_id} is missing token_uri or client_id. Credentials may not be refreshable.")
         # Depending on strictness, you might return None here too.
         # For now, allow creating credentials if access_token exists.

    try:
        creds = Credentials(
            token=decrypted_access_token,
            refresh_token=decrypted_refresh_token,
            token_uri=user.token_uri,
            client_id=decrypted_client_id,
            client_secret=decrypted_client_secret,
            scopes=decrypted_scopes
        )
        return creds
    except Exception as e:
        # Log the error that occurred during Credentials object creation
        print(f"Error creating Credentials object for user {google_id}: {e}")
        return None
