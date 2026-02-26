import os
from pathlib import Path
from dotenv import load_dotenv
from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta
from jose import jwt, JWTError # type: ignore
from typing import cast

#Finding root project folder
current_file = Path(__file__).resolve() # beckand/src/security.py
project_root = current_file.parents[2]  # ადის 2 საფეხურით მაღლა Elite_Motors_AI-მდე
env_path = project_root / ".env"

load_dotenv(dotenv_path=env_path)

#JWT configuration
SECRET_KEY=os.getenv("SECRET_KEY")
#For password hashing use bycript
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if not SECRET_KEY:
    print(f"\n[DEBUG]: search here: {env_path}")
    print(f"[DEBUG]: is file exists? {env_path.exists()}")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("CRITICAL: SECRET_KEY is missing or too short in .env file!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

def hash_password(password: str):
    #Converts password to hash
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    #Cheked if password match to hashed password
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    #Creates 5 minute JWT token
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY must be set in environment variables")

    return jwt.encode(to_encode, cast(str, SECRET_KEY), algorithm=ALGORITHM)






