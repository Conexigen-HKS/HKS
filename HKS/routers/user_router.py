
from starlette import status
from HKS.data.databaseScript.database import get_db
from HKS.data.databaseScript.models import UsersBase
from HKS.services.user_service import login, register
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/")
def user_login_router(username: str, password: str, db: Session = Depends(get_db)):
    user = login(db, username, password)
    if user:
        return dict(
            message="Login successful!"
        )
    else:
        return dict(
            message="Login failed!"
        )

@users_router.post("/register")
def user_register_router(username: str, password: str, role: str, db: Session = Depends(get_db)):
    user = register(db, username, password, role)
    if user:
        return {'username': user.user_username}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Register failed!")





