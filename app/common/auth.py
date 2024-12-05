from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.common.responses import Forbidden
from app.data.schemas.users import UserResponse
from app.config import ALGORITHM, SECRET_KEY
from sqlalchemy.orm import Session
from app.data.models import Professional, User
from app.data.database import get_db
from app.services.user_services import get_user
from app.common.utils import get_password_hash, verify_password, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
token_blacklist = set()


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({'exp': expire})
#     to_encode['role'] = data.get('role')
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
from datetime import datetime as dt, timezone, timedelta



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.now(timezone.utc) + expires_delta
    else:
        expire = dt.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["exp"] = dt.fromtimestamp(payload["exp"], timezone.utc)
        if payload["exp"] < dt.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")



def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return UserResponse.model_validate(user)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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
    if not current_user.is_admin:
        raise Forbidden("Not enough permissions")
    return current_user


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