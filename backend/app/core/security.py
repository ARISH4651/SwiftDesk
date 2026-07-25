import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "swiftdesk-super-secret-jwt-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(user_id: int, email: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a single unified JWT format with required claims:
    {
      "sub": str(user_id),
      "email": email,
      "role": role ("CUSTOMER" | "SUPPORT" | "ADMIN"),
      "iat": timestamp,
      "exp": timestamp
    }
    """
    now = datetime.utcnow()
    expire = now + (expires_delta if expires_delta else timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role.upper(),
        "iat": now,
        "exp": expire
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
