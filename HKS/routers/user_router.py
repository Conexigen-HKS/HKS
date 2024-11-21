import traceback

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional

from HKS.common.auth import create_access_token
from HKS.common.utils import verify_password, get_password_hash
from HKS.services.user_service import create_company, create_professional, get_all_users
from app.data.database import get_db
from app.data.models import User, Professional, Companies
from app.data.schemas.company import CompanyResponse, CompanyOut, CompanyRegister
from app.data.schemas.professional import ProfessionalResponse, ProfessionalRegister, ProfessionalOut
from app.data.schemas.user import Login, UserResponse

app = FastAPI()
users_router = APIRouter(prefix='/users', tags=['Users'])



@users_router.post("/register_company", response_model=CompanyResponse)
def register_company(company_data: CompanyRegister, db: Session = Depends(get_db)):
    try:
        company = create_company(db, company_data)
        return {"message": "Company registered successfully", "company": company}
    except HTTPException as e:
        raise e

@users_router.post("/register_professional")
def register_professional(professional_data: ProfessionalRegister, db: Session = Depends(get_db)):
    try:
        professional = create_professional(db, professional_data)
        return {"message": "Professional registered successfully", "professional": professional}
    except HTTPException as e:
        raise e



@users_router.get("/", response_model=List[ProfessionalOut])
def return_all_users(role: str = Query(...), db: Session = Depends(get_db)):

    try:
        users = get_all_users(db=db, role=role)
        return [
            ProfessionalOut.model_validate(user) if role == 'professional' else CompanyOut.model_validate(user)
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@users_router.post("/register", response_model=UserResponse)
def register_basic_user(user_data: ProfessionalRegister, role: Optional[str] = "basic", db: Session = Depends(get_db)):

    try:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=f"Username '{user_data.username}' is already taken.")

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            role=role,
            is_admin=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse.model_validate(new_user)
    except Exception as e:
        print(f"Unhandled Exception: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during user registration.")

@users_router.post("/login")
def login_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    try:
        user = db.query(User).filter(User.username == data.username).first()

        # Validate user credentials
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        access_token = create_access_token(data={
            "sub": user.username,
            "id": str(user.id),
            "role": user.role,
            "is_admin": user.is_admin
        })

        response = {
            "message": "Logged in successfully",
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_admin": user.is_admin
            }
        }

        return response

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Unhandled Exception Trace: {error_trace}")
        raise HTTPException(status_code=500, detail="An error occurred during login.")