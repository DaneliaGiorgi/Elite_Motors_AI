import os
from pathlib import Path
from dotenv import load_dotenv
from passlib.context import CryptContext # type: ignore
from datetime import datetime, timedelta
from jose import jwt, JWTError # type: ignore

#Finding root project folder
base_directory=Path(__file__).resolve().parent.parent
env_path = base_directory / ".env"

load_dotenv(dotenv_path=env_path)

#For password hashing use bycript
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#JWT configuration
SECRET_KEY=os.getenv("SECRET_KEY", "default_secret_key")
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
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)







