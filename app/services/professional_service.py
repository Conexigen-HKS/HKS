
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.models import User, ProfessionalProfile, CompanyOffers, Professional, RequestsAndMatches, Location
from app.data.schemas.job_application import JobApplicationResponse
from app.data.schemas.professional import ProfessionalUpdate, ProfessionalResponse


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


def get_own_job_applications(db: Session, user_id: UUID):
    print(f"Fetching Professional for user_id: {user_id}")
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()

    if not professional:
        print("No Professional found!")
        raise HTTPException(status_code=404, detail="Professional not found")

    print(f"Fetching Professional Profiles for professional_id: {professional.id}")
    applications = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional.id
    ).all()

    if not applications:
        print("No applications found for professional_id.")
        return []

    print(f"Applications found: {applications}")

    # Construct response
    result = []
    for app in applications:
        location_name = None
        if app.location_id:
            location = db.query(Location).filter(Location.id == app.location_id).first()
            location_name = location.city_name if location else None

        result.append(
            JobApplicationResponse(
                id=app.id,
                description=app.description,
                min_salary=app.min_salary,
                max_salary=app.max_salary,
                status=app.status,
                location_name=location_name,
                skills=[skill.skill.name for skill in app.skills]
            )
        )
    print(f"Job Applications Response: {result}")
    return result


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




def view_own_profile(db: Session, user_id: UUID):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return ProfessionalResponse.from_orm(professional)


def update_own_profile(db: Session, user_id: UUID, data: ProfessionalUpdate):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    if data.first_name:
        professional.first_name = data.first_name
    if data.last_name:
        professional.last_name = data.last_name
    if data.location:
        location = db.query(Location).filter(Location.city_name == data.location).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        professional.location_id = location.id
    if data.phone:
        professional.phone = data.phone
    if data.email:
        professional.email = data.email
    if data.website:
        professional.website = data.website
    if data.summary:
        professional.summary = data.summary

    db.commit()
    db.refresh(professional)
    return ProfessionalResponse.from_orm(professional)


def get_own_job_applications(db: Session, user_id: UUID):
    applications = db.query(ProfessionalProfile).filter(ProfessionalProfile.user_id == user_id).all()
    return [
        JobApplicationResponse(
            id=app.id,
            description=app.description,
            min_salary=app.min_salary,
            max_salary=app.max_salary,
            status=app.status,
            location_name=app.location.city_name if app.location else None,
            skills=[s.skill.name for s in app.skills]
        )
        for app in applications
    ]
