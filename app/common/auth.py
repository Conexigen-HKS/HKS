"""
This module contains the authentication logic for the application.
It includes functions to authenticate users, create access tokens, decode access tokens,
and check user permissions."""
from datetime import datetime as dt, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.common.responses import Forbidden
from app.common.utils import get_password_hash, verify_password, verify_token
from app.config import ALGORITHM, SECRET_KEY
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.users import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
token_blacklist = set()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token with the given data and expiration time.
    :param data: The data to encode in the token
    :param expires_delta: The expiration time of the token
    :return: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = dt.now(timezone.utc) + expires_delta
    else:
        expire = dt.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """
    Decode the given access token and return the payload.
    :param token: The access token to decode
    :return: The payload of the token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["exp"] = dt.fromtimestamp(payload["exp"], timezone.utc)
        if payload["exp"] < dt.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
    """
    Authenticate the user with the given username and password.
    :param db: The database session
    :param username: The username of the user
    :param password: The password of the user
    :return: The user response if the user is authenticated, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return UserResponse.model_validate(user)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get the current user from the given access token.
    :param token: The access token to decode
    :param db: The database session
    :return: The user object
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get('sub')
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user from the given access token.
    :param current_user: The current user object
    :return: The user object
    """
    try:
        if not current_user.is_admin:
            raise Forbidden("Not enough permissions")
        return current_user
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc


def check_permissions(user: User, required_role: str):
    """
    Check if the given user has the required role.
    :param user: The user object
    :param required_role: The required role
    """
    if user.role != required_role:
        raise Forbidden(f"Only {required_role}s can access this resource")


def hash_existing_user_passwords(db: Session):
    """
    Hash the passwords of all existing users in the database.
    :param db: The database session
    """
    users = db.query(User).all()

    for user in users:
        if len(user.hashed_password) != 60:
            user.hashed_password = get_password_hash(user.hashed_password)
            db.add(user)

    db.commit()
    print("All user passwords have been hashed successfully.")


UserAuthDep =  Annotated[User, Depends(get_current_user)]
