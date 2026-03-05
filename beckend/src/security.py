import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

#Finding the project root and loading .env
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

#JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_development_purposes_only_32_chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("CRITICAL: SECRET_KEY is missing or too short in .env file!")

#Password Management (Using Native Bcrypt)
def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the plain-text password matches the stored hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

#JWT Token Management (Using PyJWT)
def create_access_token(data: dict):
    """Generates a JWT access token valid for 30 minutes."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """Decodes the JWT token and returns the payload (sub, role, etc.)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except Exception:
        return None