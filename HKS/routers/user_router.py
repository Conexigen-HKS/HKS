from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from HKS.services.auth_service import create_jwt_token, authenticate
from HKS.services.user_service import register_user, authenticate_user, get_all_users
from app.data.database import get_db
from app.data.schemas.user import UserRegistrationRequest, UserLoginRequest, UsersListResponse

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post("/")
def register_user_route(new_usr: UserRegistrationRequest, db: Session = Depends(get_db)):
    role = "user"
    return register_user(new_usr.username, new_usr.password, role, db)


@users_router.post("/login")
def login_user_route(user: UserLoginRequest, db: Session = Depends(get_db)):
    user_data = authenticate_user(user.username, user.password, db)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_jwt_token(user_data["id"], user_data["username"], user_data["role"])
    return {"access_token": token, "token_type": "bearer"}

@users_router.get("/protected")
def protected_route(authorization: str = Depends(authenticate)):
    return {"message": "You are authorized!", "user_info": authorization}

@users_router.get("/all", response_model=UsersListResponse)
def show_all_users_route(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return {"users": users}