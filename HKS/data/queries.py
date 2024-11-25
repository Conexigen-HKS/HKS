import logging
from uuid import UUID
from venv import logger

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from HKS.data.models import User, Professional, CompanyOffers, Companies, ProfessionalProfile, Skills, \
    ProfessionalProfileSkills, RequestsAndMatches
from HKS.data.schemas.user import UserResponse


# USER QUERIES

# Create a new user
def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    try:
        user = db.query(User).filter(User.id == user_id).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat(),
        }
        return UserResponse.model_validate(user_dict)
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def user_exists(db: Session, user_id: UUID) -> bool:
    return db.query(User).filter(User.id == user_id).first() is not None

# PROFESSIONAL QUERIES
def update_user_role(db: Session, user_id: UUID, role: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
        return user
    return None

def get_professional_by_user_id(db: Session, user_id: UUID):
    return db.query(Professional).filter(Professional.user_id == user_id).first()

def create_professional_profile(db: Session, user_id: UUID, professional_data: dict):
    professional = Professional(user_id=user_id, **professional_data)
    db.add(professional)
    db.commit()
    db.refresh(professional)
    return professional

def get_professional_by_username(db: Session, username: str) -> Professional:
    return db.query(Professional).join(User).filter(User.username == username).first()

# COMPANY QUERIES
def create_company_record(db: Session, user_id: UUID, company_data: dict) -> Companies:
    company = Companies(user_id=user_id, **company_data)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_company_by_username(db: Session, username: str) -> Companies:
    return db.query(Companies).join(User).filter(User.username == username).first()

# ROLE-BASED USER LIST
def get_all_users_by_role(db: Session, role: str):
    if role == 'professional':
        return db.query(Professional, User).join(User).filter(User.role == 'professional').all()
    elif role == 'company':
        return db.query(Companies, User).join(User).filter(User.role == 'company').all()
    return []

def update_user_role(db: Session, user_id: UUID, role: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
        return user
    return None








# Query to create a new skill
def create_skill(db: Session, name: str) -> Skills:
    existing_skill = db.query(Skills).filter(Skills.name == name).first()
    if existing_skill:
        return existing_skill
    skill = Skills(name=name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

# Fetch a skill by ID
def get_skill_by_id(db: Session, skill_id: UUID4) -> Skills:
    return db.query(Skills).filter(Skills.id == skill_id).first()

def assign_skill_to_profile(db: Session, profile_id: UUID4, skill_id: UUID4, level: int) -> ProfessionalProfileSkills:
    professional_skill = ProfessionalProfileSkills(
        professional_profile_id=profile_id,
        skills_id=skill_id,
        level=level
    )
    db.add(professional_skill)
    db.commit()
    db.refresh(professional_skill)
    return professional_skill



# Query to fetch a skill by name
def get_skill_by_name(db: Session, name: str) -> Skills:
    return db.query(Skills).filter(Skills.name == name).first()



# Query to get all skills for a professional profile
def get_skills_for_profile(db: Session, profile_id: UUID):
    return db.query(ProfessionalProfileSkills, Skills).join(Skills).filter(
        ProfessionalProfileSkills.professional_profile_id == profile_id
    ).all()





def get_job_applications_by_professional(db: Session, professional_profile_id: str):

    return db.query(RequestsAndMatches).filter(RequestsAndMatches.professional_profile_id == professional_profile_id).all()


