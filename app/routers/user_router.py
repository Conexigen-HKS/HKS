from typing import Literal
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.cloudinary_service import ALLOWED_EXTENSIONS, change_picture, delete_picture
from app.data.models import Companies, Professional, User
from app.data.database import get_db
from app.common import auth
from app.data.schemas.users import CompanyRegister, ProfessionalRegister, TokenResponse
from app.services.user_services import create_company, create_professional, get_all_users

app = FastAPI()

users_router = APIRouter(prefix='/api/users', tags=['Users'])

@users_router.post("/register/company")
def register_company(company_data: CompanyRegister, db: Session = Depends(get_db)):
    try:
        company = create_company(db, company_data)
        return {"message": "Company registered successfully"}
    except HTTPException as e:
        raise e
    
@users_router.post("/register/professional")
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
    
    user = db.query(User).filter(User.username == data.username).first()

    if user.role == 'professional':
        prof = db.query(Professional).filter(Professional.user_id == user.id).first()
        if prof.status == 'blocked':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Your account has been blocked. Please contact the administrator for more information.'
            )
        
    elif user.role == 'company':
        comp = db.query(Companies).filter(Companies.user_id == user.id).first()
        if comp.status == 'blocked':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Your account has been blocked. Please contact the administrator for more information.'
            )
        
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

@users_router.post("/picture")
async def upload_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file format. Allowed formats: jpg, jpeg, png.")

    if current_user.role == 'admin':
        raise HTTPException(status_code=400, detail="Admins cannot have a profile picture")

    try:
        result = change_picture(current_user, db, file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@users_router.delete("/picture")
def remove_picture(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    try:
        return delete_picture(current_user=current_user, db=db)
    except Exception as e:
        return {"error": "Failed to delete picture", "details": str(e)}
    

@users_router.put("/picture")
async def change_user_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    if file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
        return {"error": "Invalid file format. Allowed formats: jpg, jpeg, png."}

    result = change_picture(current_user, db, file)
    return result