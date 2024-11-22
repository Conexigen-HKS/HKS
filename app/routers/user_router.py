from typing import Literal
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from data.database import get_db
from common import auth
from data.schemas.users import CompanyRegister, ProfessionalRegister, TokenResponse
from services.user_services import create_company, create_professional, get_all_users
from common.responses import BadRequest

app = FastAPI()

users_router = APIRouter(prefix='/api/users', tags=['Users'])

@users_router.post("/register_company")
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

#ТРЯБВА ДА СЕ ДОБАВИ id от User
@users_router.get("/")
def return_all_users(
    role: Literal['professional', 'company'] = Query(...),
    db: Session = Depends(get_db)
    ):
    print("Role received:", role)
    users = get_all_users(db=db, role=role)

    if not users:
        return []
    return users

@users_router.post('/login', response_model=TokenResponse)
def login_user(
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    
    access_token = auth.create_access_token(data={
        'sub': user.username,
        'id': str(user.id),
        'role': user.role,
        'is_admin': user.is_admin
    })

    return TokenResponse(access_token=access_token, token_type='bearer')

@users_router.post('/logout')
def logout_user(
    token: str = Depends(auth.oauth2_scheme)
):
    if not token:
        raise HTTPException(status_code=401, detail="No user is currently logged in.")
    
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    
    auth.token_blacklist.add(token)

    return {"detail": "Logged out successfully"}
