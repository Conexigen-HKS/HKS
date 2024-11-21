import traceback
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from HKS.common.utils import get_password_hash, ValidUsername, ValidPassword
from app.data.models import Professional, User, Companies
from app.data.schemas.company import CompanyRegister, CompanyResponse
from app.data.schemas.professional import ProfessionalResponse, ProfessionalRegister
from app.data.schemas.user import UserResponse


def get_user(db: Session, username: str) -> UserResponse:
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)


def create_professional(db: Session, professional_data: ProfessionalRegister) -> ProfessionalResponse:
    hashed_password = get_password_hash(professional_data.password)

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

        return ProfessionalResponse.model_validate(professional)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error occurred while creating professional: {str(e)}")


def get_professional(db: Session, username: str) -> ProfessionalResponse:
    professional = (
        db.query(Professional)
        .join(User, Professional.user_id == User.id)
        .filter(User.username == username)
        .first()
    )

    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    return ProfessionalResponse.model_validate(professional)

def create_company(db: Session, company_data: CompanyRegister) -> dict:
    hashed_password = get_password_hash(company_data.password)

    existing_user = db.query(User).filter(User.username == company_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"Username '{company_data.username}' is already taken.")

    existing_company = db.query(Companies).filter(Companies.name == company_data.company_name).first()
    if existing_company:
        raise HTTPException(status_code=400, detail=f"Company name '{company_data.company_name}' is already taken.")

    try:
        # Create the User
        user = User(username=company_data.username, hashed_password=hashed_password, role="company")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create the Company
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

        return {
            "id": company.id,
            "name": company.name,
            "address": company.address,
            "description": company.description,
            "is_approved": company.is_approved,
            "contacts": company.contacts,
            "username": user.username,
            "user_id": user.id
        }
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Duplicate entry detected for username or company name.")
    except Exception as e:
        db.rollback()
        print(f"General Exception: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


def get_company(db: Session, username: str) -> CompanyResponse:
    company = (
        db.query(Companies)
        .join(User, Companies.user_id == User.id)
        .filter(User.username == username)
        .first()
    )

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Include username in the response
    return CompanyResponse(
        id=company.id,
        name=company.name,
        address=company.address,
        description=company.description,
        is_approved=company.is_approved,
        username=company.user.username  # Ensure this is accessible
    )


def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)


def get_all_users(db: Session, role: str) -> List:
    if role == 'professional':
        all_entities = (
            db.query(Professional, User)
            .join(User, Professional.user_id == User.id)
            .filter(User.role == 'professional')
            .all()
        )

        return [
            ProfessionalResponse.model_validate(entity)
            for entity, _ in all_entities
        ] if all_entities else []

    elif role == 'company':
        all_entities = (
            db.query(Companies, User)
            .join(User, Companies.user_id == User.id)
            .filter(User.role == 'company')
            .all()
        )

        return [
            CompanyResponse.model_validate(entity)
            for entity, _ in all_entities
        ] if all_entities else []

    else:
        raise HTTPException(status_code=400, detail="Invalid role. Role must be 'professional' or 'company'")


def get_username_from_id(usr_id: UUID, db: Session) -> str:
    user = db.query(User).filter(User.id == usr_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {usr_id} not found!")
    return user.username


def user_exists(id: UUID, db: Session) -> bool:
    return db.query(User).filter(User.id == id).first() is not None
