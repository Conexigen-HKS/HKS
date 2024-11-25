from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException
import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


from app.common.responses import Forbidden
from app.common.utils import verify_password, verify_token, get_password_hash
from HKS.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from HKS.data.database import get_db
from HKS.data.models import User
from HKS.data.queries import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login', auto_error=False)
token_blacklist = set()



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    to_encode['role'] = data.get('role')
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


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


UserAuthDep = Annotated[User, Depends(get_current_user)]


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