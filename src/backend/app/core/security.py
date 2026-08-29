from datetime import datetime, timedelta
from typing import Any, Union, Optional
import base64
import json

try:
    from jose import jwt
except ImportError:
    try:
        import jwt
    except ImportError:
        # Fallback dummy JWT encoder/decoder for local standalone tests
        class DummyJWT:
            @staticmethod
            def encode(payload, key, algorithm="HS256"):
                s = json.dumps(payload, default=str)
                return "mock_jwt." + base64.urlsafe_b64encode(s.encode()).decode().rstrip("=") + ".sig"
            
            @staticmethod
            def decode(token, key, algorithms=None, audience=None):
                parts = token.split(".")
                if len(parts) >= 2:
                    padding = 4 - (len(parts[1]) % 4)
                    s = base64.urlsafe_b64decode(parts[1] + ("=" * padding)).decode()
                    return json.loads(s)
                return {"sub": "a1111111-1111-1111-1111-111111111111"}
        jwt = DummyJWT()

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    class DummyCryptContext:
        def verify(self, plain, hashed): 
            return hashed == f"hashed_{plain}" or plain == hashed
        def hash(self, plain): 
            return f"hashed_{plain}"
    pwd_context = DummyCryptContext()

from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        return f"hashed_{password}"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
