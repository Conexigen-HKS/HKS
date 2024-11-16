from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from common.responses import Forbidden
from data.schemas.user import UserResponse
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from sqlalchemy.orm import Session
from services.user_services import get_user
from data.models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
token_blacklist = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    if token in token_blacklist:
        raise Forbidden("Token has been revoked")

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub') if payload else None
        if username is None:
            return None
        return payload
    except JWTError:
            return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return UserResponse.model_validate(user)

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    payload = verify_token(token)
    username = payload.get('sub') if payload else None
    if not username:
        return None
    return get_user(username)

def get_current_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise Forbidden('You do not have permission to access this')
    return user

def hash_existing_user_passwords(db: Session):
    users = db.query(User).all()
    
    for user in users:
        if len(user.hashed_password) != 60:
            user.hashed_password = get_password_hash(user.hashed_password)
            db.add(user)
    
    db.commit()
    print("All user passwords have been hashed successfully.")

UserAuthDep =  Annotated[User, Depends(get_current_user)]
