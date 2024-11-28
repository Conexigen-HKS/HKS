
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.models import User, ProfessionalProfile, CompanyOffers,  Professional, RequestsAndMatches
from app.data.schemas.professional import ProfessionalUpdate




def get_professional_by_user_id(db: Session, user_id: UUID):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return professional

def get_professional_service(db: Session, user_id: UUID):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return professional

def update_professional_service(db: Session, user_id: UUID, update_data: ProfessionalUpdate):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    # Update allowed fields
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(professional, key, value)

    db.commit()
    db.refresh(professional)
    return professional

def view_professional_profile(db: Session, user_id: UUID):
    profile = get_professional_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile



def update_professional_status_on_match(db: Session, professional_profile_id: UUID):
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == professional_profile_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    has_matches = db.query(RequestsAndMatches).filter(
        RequestsAndMatches.professional_profile_id == professional_profile_id
    ).count()

    if has_matches > 0:
        profile.status = "busy"
    else:
        profile.status = "active"

    db.commit()
    return profile




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