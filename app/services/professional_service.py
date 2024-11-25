from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.common.utils import get_password_hash
from HKS.data.models import User, ProfessionalProfile, CompanyOffers, CompaniesRequirements, Professional
from HKS.data.queries import get_professional_by_user_id, \
    get_user_by_username, update_user_role, get_user_by_id, create_professional_profile


def create_professional_service(db: Session, professional_data, username: str):
    user = get_user_by_username(db, username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    hashed_password = get_password_hash(professional_data.password)
    user = User(
        username=professional_data.username,
        hashed_password=hashed_password,
        role="professional"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    professional_dict = {
        "first_name": professional_data.first_name,
        "last_name": professional_data.last_name,
        "address": professional_data.address,
        "summary": professional_data.summary,
        "is_approved": False,
    }
    return create_professional_profile(db, user.id, professional_dict)


def view_professional_profile(db: Session, user_id: UUID):
    profile = get_professional_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile



def upgrade_user_to_professional_service(db: Session, user_id: UUID, professional_data):

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.role != "basic":
        raise HTTPException(status_code=400, detail="Only basic users can be upgraded to professional.")

    update_user_role(db, user_id, "professional")

    professional = create_professional_profile(db, user_id, {
        "first_name": professional_data.first_name,
        "last_name": professional_data.last_name,
        "address": professional_data.address,
        "summary": professional_data.summary,
        "is_approved": False,
        "status": "active",
    })

    professional_profile = ProfessionalProfile(
        user_id=user_id,
        professional_id=professional.id,
        status="active"
    )
    db.add(professional_profile)
    db.commit()
    db.refresh(professional_profile)

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "professional_profile": {
            "id": professional_profile.id,
            "status": professional_profile.status,
            "first_name": professional_data.first_name,
            "last_name": professional_data.last_name,
            "address": professional_data.address,
            "summary": professional_data.summary
        }
    }




def create_company_offer(db: Session, company_id: str, min_salary: int, max_salary: int, location: str, description: str, requirements: List[dict]):

    company_offer = CompanyOffers(
        company_id=company_id,
        type="company",
        status="active",
        min_salary=min_salary,
        max_salary=max_salary,
        location=location,
        description=description
    )
    db.add(company_offer)
    db.commit()
    db.refresh(company_offer)

    for req in requirements:
        company_requirement = CompaniesRequirements(
            company_offers_id=company_offer.id,
            requirements_id=req["requirements_id"],
            level=req.get("level", 0)
        )
        db.add(company_requirement)

    db.commit()
    db.refresh(company_offer)
    return company_offer


def create_professional_application(db: Session, professional_profile_id: str, min_salary: int, max_salary: int, location: str, description: str):

    professional_application = CompanyOffers(
        professional_profile_id=professional_profile_id,
        type="professional",
        status="active",
        min_salary=min_salary,
        max_salary=max_salary,
        location=location,
        description=description
    )
    db.add(professional_application)
    db.commit()
    db.refresh(professional_application)
    return professional_application

def get_professional_profile_for_user(db: Session, user_id: str):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    professional_profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional.id
    ).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    return professional_profile
