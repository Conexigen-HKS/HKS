from uuid import UUID
from sqlalchemy.orm import Session
from data.schemas.company import CompanyResponse
from data.schemas.professional import ProfessionalResponse
from common import auth
from data.models import Professional, User, Companies
from data.schemas.user_register import UserResponse
from common.auth import verify_token, oauth2_scheme
from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from data.schemas.user_register import CompanyRegister, ProfessionalRegister


def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    payload = verify_token(token)
    username = payload.get('sub') if payload else None
    if not username:
        return None
    
    return db.query(User).filter(User.username == username).first()
    
def create_professional(db: Session, professional_data: ProfessionalRegister) -> Professional:
    hashed_password = auth.get_password_hash(professional_data.password)

    try:
        user = User(username=professional_data.username, hashed_password=hashed_password, role="professional")
        db.add(user)
        db.commit()
        db.refresh(user)

        professional = Professional(
            user_id=user.id,
            first_name=professional_data.first_name,
            last_name=professional_data.last_name,
            address=professional_data.address,
            summary=professional_data.summary,
            is_approved=False
        )

        db.add(professional)
        db.commit()
        db.refresh(professional)

        return professional

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error occurred while creating professional: {str(e)}")
    
def get_professional(db: Session, username: str) -> Professional:
    professional = db.query(Professional).filter(Professional.username == username).first()

    if not professional:
        return None
    
    return professional

def return_professional_response():#трябва да се създаде проф модел в пайдантик
    raise NotImplementedError

def create_company(db: Session, company_data: CompanyRegister) -> Companies:
    hashed_password = auth.get_password_hash(company_data.password)

    try:
        user = User(username=company_data.username, hashed_password=hashed_password, role="company")
        db.add(user)
        db.commit()
        db.refresh(user)

        company = Companies(
            user_id=user.id,
            name=company_data.company_name,
            description=company_data.description,
            address=company_data.address,
            contacts="",
            is_approved=False
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error occurred while creating company: {str(e)}")


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
                username=user.username,
                first_name=entity.first_name,
                last_name=entity.last_name,
                address=entity.address,
                status=entity.status,
                summary=entity.summary,
                is_approved=entity.is_approved,
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
                username=user.username,
                name=entity.name,
                address=entity.address,
                description=entity.description,
                contacts=entity.contacts,
                is_approved=entity.is_approved,
            )
            for entity, user in all_entities
        ] if all_entities else []

    else:
        return []

def get_username_from_id(usr_id: str, db: Session):
    user = db.query(User).filter(User.id == usr_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {usr_id} not found !")
    return user.username

def user_exists(id: str, db: Session):
    user = db.query(User).filter(User.id == id).first()
    return True if user else False