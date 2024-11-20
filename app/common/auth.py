from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from common.responses import Forbidden
from data.schemas.user_register import UserResponse
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from sqlalchemy.orm import Session
from data.models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
token_blacklist = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({'exp': expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    to_encode['role'] = data.get('role')  # Добавяме role в токена
    to_encode['is_admin'] = data.get('is_admin', False)  # Добавяме is_admin в токена
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def verify_token(token: str):
#     if token in token_blacklist:
#         raise Forbidden("Token has been revoked")

#     if not token:
#         return None

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get('sub') if payload else None
#         if username is None:
#             return None
#         return payload
#     except JWTError:
#             return None

def verify_token(token: str):
    if token in token_blacklist:
        raise Forbidden("Token has been revoked")

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub') if payload else None
        role = payload.get('role')  # Ролята на потребителя
        is_admin = payload.get('is_admin')  # Проверка за администратор

        if username is None or role is None:
            return None
        return payload
    except JWTError:
        return None


# def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
#     user = db.query(User).filter(User.username == username).first()

#     if not user or not verify_password(password, user.hashed_password):
#         return None
    
#     return UserResponse.from_orm(user)

def authenticate_user(db: Session, username: str, password: str, role: str) -> Optional[UserResponse]:
    user = db.query(User).filter(User.username == username, User.role == role).first()

    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return UserResponse.model_validate(user)

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     if not token:
#         return None
#     payload = verify_token(token)
#     username = payload.get('sub') if payload else None
#     if not username:
#         return None
#     return get_user(username)


def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    payload = verify_token(token)
    username = payload.get('sub') if payload else None
    role = payload.get('role')
    is_admin = payload.get('is_admin')

    if not username or not role:
        return None
    from app.services.user_services import get_user
    return get_user(username)


def get_current_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise Forbidden('You do not have permission to access this')
    return user

UserAuthDep =  Annotated[User, Depends(get_current_user)]

def check_permissions(user: User, required_role: str):
    if user.role != required_role:
        raise Forbidden(f"Only {required_role}s can access this resource")

def hash_existing_user_passwords(db: Session):
    users = db.query(User).all()
    
    for user in users:
        if len(user.hashed_password) != 60:
            user.hashed_password = get_password_hash(user.hashed_password)
            db.add(user)
    
    db.commit()
    print("All user passwords have been hashed successfully.")