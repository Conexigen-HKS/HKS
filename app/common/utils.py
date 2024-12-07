"""
This module contains the utility functions for the application
such as password hashing, password verification, and token verification.
"""
import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import SECRET_KEY, ALGORITHM

ValidUsername = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
ValidPassword = re.compile(r'^[a-zA-Z0-9!@$_?.]{8,}$')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__ident="2b")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the password hash
    Accepts:
        plain_password: str
        hashed_password: str
    Returns:
        bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Get the password hash
    Accepts:
        password: str
    Returns:
        str
    """
    return pwd_context.hash(password)

def verify_token(token: str):
    """
    Verify the token
    Accepts:
        token: str
    Returns:
        dict
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

