import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM

ValidUsername = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
ValidPassword = re.compile(r'^[a-zA-Z0-9!@$_?.]{8,}$')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__ident="2b")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None