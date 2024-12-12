"""
This module contains functions and classes related to authentication and authorization.
Methods for creating and decoding JWT tokens, authenticating users,
and checking permissions are included.
"""

from datetime import datetime as dt
from datetime import timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session

from app.common.responses import Forbidden
from app.common.utils import get_password_hash, verify_password
from app.config import ALGORITHM, SECRET_KEY
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.users import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)
token_blacklist = set()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT token with the given data and expiration time.
    Accepts a dictionary of data to encode and an optional expiration time.
    If no expiration time is provided, the token will expire in X hour.
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
    Decode the given JWT token and return the payload.
    If the token is invalid or expired, raise an HTTPException
    with a 401 status code.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") < dt.now(timezone.utc).timestamp():
            raise HTTPException(status_code=401, detail="Token has expired")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}") from e


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[UserResponse]:
    """
    Authenticate the user with the given username and password.
    If the user is not found or the password is incorrect, return None.
    Otherwise, return the user data as a UserResponse object.
    """
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None

    return UserResponse.model_validate(user)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get the current user from the request cookies.
    If no token is provided, return None.
    If the token is invalid or expired, return None.
    Otherwise, return the user object.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None  # Allow unauthenticated access

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        payload = decode_access_token(token)
        username = payload.get("sub")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None  # Return None if user not found
        return user
    except HTTPException:
        return None  # Return None if token is invalid or expired


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user from the request cookies.
    If no token is provided, raise an HTTPException.
    If the token is invalid or expired, raise an HTTPException.
    If the user is not an admin, raise an HTTPException.
    Otherwise, return the user object.
    """
    if not current_user.is_admin:
        raise Forbidden("Not enough permissions")
    return current_user


UserAuthDep = Annotated[User, Depends(get_current_user)]


def check_permissions(user: User, required_role: str):
    """
    Check if the given user has the required role.
    If the user does not have the required role, raise a Forbidden exception.
    """
    if user.role != required_role:
        raise Forbidden(f"Only {required_role}s can access this resource")


def hash_existing_user_passwords(db: Session):
    """
    Hash all existing user passwords in the database.
    This function should be used to hash all existing user passwords
    when the hashing algorithm is changed or updated.
    """
    users = db.query(User).all()

    for user in users:
        if len(user.hashed_password) != 60:
            user.hashed_password = get_password_hash(user.hashed_password)
            db.add(user)

    db.commit()
    print("All user passwords have been hashed successfully.")
