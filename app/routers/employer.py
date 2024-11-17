from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, UUID4
from sqlalchemy.orm import Session
from app.data.database import get_db
from app.services.user_services import create_user, get_user, get_all_users

users_router = APIRouter(prefix='/users', tags=["Users"])


class UserSchema(BaseModel):
    id: UUID4
    username: str
    is_admin: bool
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreateSchema(BaseModel):
    username: str
    hashed_password: str
    role: Optional[str] = "professional"
    is_admin: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
@users_router.post("/", response_model=UserSchema)
def create_user_endpoint(username: str, hashed_password: str, db: Session = Depends(get_db)):
    return create_user(db, username, hashed_password)

@users_router.get("/{user_id}", response_model=UserSchema)
def get_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@users_router.get("/", response_model=List[UserSchema])
def get_all_users_endpoint(db: Session = Depends(get_db)):
    return get_all_users(db)
