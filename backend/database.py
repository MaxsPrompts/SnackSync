import os
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    encrypted_youtube_access_token = Column(LargeBinary, nullable=True)
    encrypted_youtube_refresh_token = Column(LargeBinary, nullable=True)
    # New fields for storing more comprehensive credential details
    token_uri = Column(String, nullable=True)
    client_id_g = Column(LargeBinary, nullable=True) # Encrypted string
    client_secret_g = Column(LargeBinary, nullable=True) # Encrypted string
    scopes_g = Column(LargeBinary, nullable=True) # Encrypted JSON string of list of scopes

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# Example of how to get a DB session, can be used in crud.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
