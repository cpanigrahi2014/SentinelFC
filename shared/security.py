"""Shared security utilities: JWT, encryption, RBAC."""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .schemas import TokenPayload, UserAuth, UserRole

# --- Configuration ---

SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

security_scheme = HTTPBearer()


# --- JWT Token Management ---

def create_access_token(user: UserAuth, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            role=UserRole(payload["role"]),
            exp=datetime.fromtimestamp(payload["exp"]),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> TokenPayload:
    return decode_token(credentials.credentials)


# --- Role-Based Access Control ---

def require_roles(*allowed_roles: UserRole):
    """Dependency that checks if the current user has one of the allowed roles."""
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


# --- Data Encryption ---

class DataEncryptor:
    """AES-256 encryption for sensitive data fields."""

    def __init__(self, key: Optional[str] = None):
        self._fernet = Fernet(key or ENCRYPTION_KEY)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()


# --- Hashing Utilities ---

def hash_pii(value: str) -> str:
    """One-way hash for PII data used in matching/deduplication."""
    salt = os.getenv("PII_HASH_SALT", "actimize-default-salt")
    return hmac.new(
        salt.encode(), value.encode(), hashlib.sha256
    ).hexdigest()
