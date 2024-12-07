from http import client
from typing import Literal
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, Request, UploadFile, Form, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app.common.auth import authenticate_user, create_access_token
from app.services.cloudinary_service import ALLOWED_EXTENSIONS, change_picture, delete_picture
from app.data.models import User
from app.data.database import get_db
from app.common import auth
from app.data.schemas.users import CompanyRegister, ProfessionalRegister
from app.services.user_services import create_company, create_professional, get_all_users

app = FastAPI()

users_router_web= APIRouter(prefix='/users', tags=['Users'])

templates = Jinja2Templates(directory="app/templates")


@users_router_web.get("/register")
def render_registration_page(request: Request, form_type: str = "professional", message: str = None):
    return templates.TemplateResponse(
        "register.html", {"request": request, "form_type": form_type, "message": message}
    )


@users_router_web.post("/register/company")
def register_company(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        company_name: str = Form(...),
        description: str = Form(...),
        location: str = Form(...),
        phone: str = Form(None),
        email: str = Form(None),
        website: str = Form(None),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": "company", "message": "Passwords do not match"}
        )

    try:
        company_data = CompanyRegister(
            username=username,
            password=password,
            company_name=company_name,
            description=description,
            location=location,
            phone=phone,
            email=email,
            website=website
        )
        create_company(db, company_data)
        return RedirectResponse(url="/api/users/login", status_code=303)
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": "company", "message": e.detail}
        )


@users_router_web.post("/register/professional")
def register_professional(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        location: str = Form(...),
        phone: str = Form(None),
        email: str = Form(None),
        website: str = Form(None),
        summary: str = Form(...),
        db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": "professional", "message": "Passwords do not match"}
        )

    try:
        professional_data = ProfessionalRegister(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            location=location,
            phone=phone,
            email=email,
            website=website,
            summary=summary
        )
        create_professional(db, professional_data)
        return RedirectResponse(url="/api/users/login", status_code=303)
    except ValidationError as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": "professional", "message": str(e)}
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": "professional", "message": e.detail}
        )


# ТРЯБВА ДА СЕ ДОБАВИ id от User
@users_router_web.get("/")
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


@users_router_web.get("/login", response_class=HTMLResponse)
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@users_router_web.post("/login", response_model=dict)
def login_user(
        response: Response,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate the access token
    access_token = create_access_token(data={
        "sub": user.username,
        "id": str(user.id),
        "role": user.role,
        "is_admin": user.is_admin
    })

    # Set the token in an HTTP-only cookie
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="Lax"
    )
    return response


@users_router_web.post('/logout')
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


@users_router_web.post("/picture")
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


@users_router_web.delete("/picture")
def remove_picture(
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    try:
        return delete_picture(current_user=current_user, db=db)
    except Exception as e:
        return {"error": "Failed to delete picture", "details": str(e)}


@users_router_web.put("/picture")
async def change_user_picture(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    if file.filename.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
        return {"error": "Invalid file format. Allowed formats: jpg, jpeg, png."}

    result = change_picture(current_user, db, file)
    return result


@users_router_web.post("/process-register")
async def process_register(request: Request):
    form_data = await request.form()
    form_type = form_data.get("form_type")
    endpoint = "/api/users/register/professional" if form_type == "professional" else "/api/users/register/company"
    response = await client.post(endpoint, data=form_data)

    if response.status_code == 200:
        return RedirectResponse("/login", status_code=302)
    else:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "form_type": form_type, "error": response.json().get("detail")}
        )

