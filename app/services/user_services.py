# app/services/user_services.py
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.data.models import Location, Professional, User, Companies
from app.data.schemas.users import UserResponse, CompanyRegister, ProfessionalRegister
from app.data.schemas.company import CompanyResponse
from app.data.schemas.professional import ProfessionalResponse
from app.common.utils import get_password_hash

def get_user(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()
    
def create_professional(db: Session, professional_data: ProfessionalRegister) -> Professional:
    hashed_password = get_password_hash(professional_data.password)

    with db.begin():

        if db.query(User).filter(User.username == professional_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{professional_data.username}' is already taken. Please choose another one."
            )
        
        if db.query(Professional).filter(Professional.email == professional_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The email '{professional_data.email}' is already used. Please use another one."
            )
        
        if db.query(Professional).filter(Professional.website == professional_data.website).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The website '{professional_data.website}' is already in use. Please use another one."
            )

        if db.query(Professional).filter(Professional.phone == professional_data.phone).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The phone number '{professional_data.phone}' is already in use. Please use another one."
            )
        
        location = db.query(Location).filter(Location.city_name == professional_data.location).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location '{professional_data.location}' does not exist.")

        
        user = User(username=professional_data.username, hashed_password=hashed_password, role="professional")
        db.add(user)
        db.flush()

        professional = Professional(
        user_id=user.id,
        first_name=professional_data.first_name,
        last_name=professional_data.last_name,
        location_id=location.id,
        summary=professional_data.summary,
        phone=professional_data.phone,
        email=professional_data.email,
        website=professional_data.website,
        is_approved=False
        )

        db.add(professional)
        db.flush()
        db.refresh(professional)

        return professional

def get_professional(db: Session, username: str) -> Professional:
    professional = db.query(Professional).filter(Professional.username == username).first()

    if not professional:
        return None
    
    return professional

def return_professional_response():#трябва да се създаде проф модел в пайдантик
    raise NotImplementedError

def create_company(db: Session, company_data: CompanyRegister) -> Companies:
    hashed_password = get_password_hash(company_data.password)

    with db.begin():

        if db.query(User).filter(User.username == company_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{company_data.username}' is already taken. Please choose another one."
            )

        if db.query(Companies).filter(Companies.email == company_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The email '{company_data.email}' is already used. Please use another one."
            )

        if db.query(Companies).filter(Companies.phone == company_data.phone).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The phone number '{company_data.phone}' is already in use. Please use another one."
            )
        
        if db.query(Companies).filter(Companies.website == company_data.website).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The website '{company_data.website}' is already in use. Please use another one."
            )

        location = db.query(Location).filter(Location.city_name == company_data.location).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location '{company_data.location}' does not exist."
            )
        
        company_name = db.query(Companies).filter(Companies.name == company_data.company_name).first()
        if company_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The company name '{company_data.company_name}' is already in use. Please use another one."
            )

        user = User(username=company_data.username, hashed_password=hashed_password, role="company")
        db.add(user)
        db.flush()

        company = Companies(
            user_id=user.id,
            name=company_data.company_name,
            description=company_data.description,
            location_id=location.id,
            contacts="",
            phone=company_data.phone,
            email=company_data.email,
            website=company_data.website,
            is_approved=False
        )
        db.add(company)
        db.flush()
        db.refresh(company)

    return company


def get_company(db: Session, username: str) -> Companies:
    company = db.query(Companies).filter(Companies.username == username).first()

    if not company:
        return None
    
    return company

def return_company_response():#трябва да се създаде компани модел в пайдантик
    raise NotImplementedError

def get_user_by_id(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None
    
    return UserResponse.model_validate(user)

def get_all_users(db: Session, role: str):
    print("Role inside get_all_entities:", role)
    if role == 'professional':
        all_entities = (
            db.query(Professional, User)
            .join(User, Professional.user_id == User.id)
            .filter(User.role == 'professional')
            .all()
        )
        return [
            ProfessionalResponse(
                id=entity.id,
                username=user.username,
                first_name=entity.first_name,
                last_name=entity.last_name,
                location=entity.location.city_name if entity.location else None,
                status=entity.status,
                phone=entity.phone,
                email=entity.email,
                website=entity.website,
                summary=entity.summary,
                is_approved=entity.is_approved,
                user_id=user.id
            )
            for entity, user in all_entities
        ] if all_entities else []

    elif role == 'company':
        all_entities = (
            db.query(Companies, User)
            .join(User, Companies.user_id == User.id)
            .filter(User.role == 'company')
            .all()
        )

        return [
            CompanyResponse(
                id=entity.id,
                name=entity.name,
                location=entity.location.city_name if entity.location else None,
                description=entity.description,
                contacts=entity.contacts,
                phone=entity.phone,
                email=entity.email,
                website=entity.website,
                is_approved=entity.is_approved,
                username=user.username,
                user_id=user.id
            )
            for entity, user in all_entities
        ] if all_entities else []

    else:
        raise HTTPException(status_code=400, detail="Invalid role")

def get_username_from_id(usr_id: str, db: Session):
    user = db.query(User).filter(User.id == usr_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {usr_id} not found !")
    return user.username

def user_exists(id: str, db: Session):
    user = db.query(User).filter(User.id == id).first()
    return True if user else False