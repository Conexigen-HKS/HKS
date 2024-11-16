from uuid import UUID
from sqlalchemy.orm import Session
from app.data.models import User
from app.data.schemas.user import UserResponse
from common.auth import verify_token, oauth2_scheme
from fastapi import Depends

def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    payload = verify_token(token)
    username = payload.get('sub') if payload else None
    if not username:
        return None
    
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: UUID) -> UserResponse:
    user =  db.query(User).filter(User.id == user_id).first() 

    if not user:
        return None
    
    return UserResponse.model_validate(user)

def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None
    
    return UserResponse.model_validate(user)

def get_all_users(db: Session):
    all_users =  db.query(User).all()

    if not all_users:
        return []
    
    return [UserResponse.model_validate(user) for user in all_users] if all_users else []
