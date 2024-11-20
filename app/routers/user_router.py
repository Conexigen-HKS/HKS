from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from data.database import get_db
from common import auth
from data.schemas.user_register import CompanyRegister, ProfessionalRegister
from services.user_services import create_company, create_professional, get_all_users, get_all_professionals
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

@users_router.get("/")
def return_all_users(db: Session = Depends(get_db)):
    users = get_all_users(db)

    if not users:
        return []
    return users

@users_router.get("/professionals")
def return_all_professionals(db: Session = Depends(get_db)):
    professionals = get_all_professionals(db)

    if not professionals:
        return []
    return professionals