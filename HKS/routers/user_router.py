
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from HKS.common import auth
from HKS.services.user_service import register_basic_user_service
from app.data.database import get_db
from app.data.schemas.user import TokenResponse, UserResponse, UserModel

app = FastAPI()

users_router = APIRouter(prefix='/users', tags=['Users'])

@users_router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserModel,
    db: Session = Depends(get_db)
):

    response = register_basic_user_service(db, user_data.dict())
    return response

#
# @users_router.post("/register_company")
# def register_company(company_data: CompanyRegister, db: Session = Depends(get_db)):
#     try:
#         company = create_company(db, company_data)
#         return {"message": "Company registered successfully", "company": company}
#     except HTTPException as e:
#         raise e
#




# @users_router.get("/")
# def return_all_users(
#         role: Literal['professional', 'company'] = Query(...),
#         db: Session = Depends(get_db)
# ):
#     print("Role received:", role)
#     users = get_all_users(db=db, role=role)
#
#     if not users:
#         return []
#     return users


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


#
# @users_router.post("/me/picture")
# async def upload_picture(
#     file: UploadFile = File(...),
#     current_user: User = Depends(auth.get_current_user),
#     db: Session = Depends(get_db)
# ):
#     try:
#         upload_result = upload_image_to_cloudinary(file.file)
#         file_url = upload_result["secure_url"]
#
#         professional = db.query(Professional).filter_by(user_id=current_user.id).first()
#         if not professional:
#             raise HTTPException(status_code=404, detail="Professional profile not found")
#
#         professional.picture = file_url
#         db.commit()
#
#         return {
#             "message": "Picture uploaded successfully",
#             "picture_url": file_url,
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))