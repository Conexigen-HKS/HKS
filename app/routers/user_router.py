from typing import Literal
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from HKS.data.database import get_db
from HKS.data.models import User, Professional
from HKS.data.schemas.user import CompanyRegister, ProfessionalRegister, TokenResponse
from app.common import auth
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.user_service import create_company, create_professional, get_all_users

app = FastAPI()

users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post("/register/company")
def register_company(company_data: CompanyRegister, db: Session = Depends(get_db)):
    try:
        company = create_company(db, company_data)
        return {"message": "Company registered successfully", "company": company}
    except HTTPException as e:
        raise e


@users_router.post("/register/professional")
def register_professional(professional_data: ProfessionalRegister, db: Session = Depends(get_db)):
    try:
        professional = create_professional(db, professional_data)
        return {"message": "Professional registered successfully", "professional": professional}
    except HTTPException as e:
        raise e


# ТРЯБВА ДА СЕ ДОБАВИ id от User
@users_router.get("/")
def return_all_users(
        role: Literal['professional', 'company'] = Query(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    if current_user.is_admin:
        users = get_all_users(db=db, role=role)

        if not users:
            return []
        return users
    else:
        raise HTTPException(status_code=403, detail="You are not authorized to view all users.")


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


@users_router.post("/me/picture")
async def upload_picture(
        file: UploadFile = File(...),
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    try:
        upload_result = upload_image_to_cloudinary(file.file)
        file_url = upload_result["secure_url"]

        professional = db.query(Professional).filter_by(user_id=current_user.id).first()
        if not professional:
            raise HTTPException(status_code=404, detail="Professional profile not found")

        professional.picture = file_url
        db.commit()

        return {
            "message": "Picture uploaded successfully",
            "picture_url": file_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))