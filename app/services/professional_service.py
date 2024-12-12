from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.data.models import User, ProfessionalProfile, CompanyOffers, Professional, RequestsAndMatches, Location
from app.data.schemas.job_application import JobApplicationResponse
from app.data.schemas.professional import ProfessionalUpdate, ProfessionalResponse
from app.data.schemas.skills import SkillResponse


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

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(professional, key, value)

    db.commit()
    db.refresh(professional)
    return professional


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


def create_professional_application(db: Session, professional_profile_id: str, min_salary: int, max_salary: int,
                                    location: str, description: str):
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


# WORKS
def view_own_profile(db: Session, user_id: UUID):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return ProfessionalResponse.from_orm(professional)


# WORKS
def update_own_profile(db: Session, user_id: UUID, data: ProfessionalUpdate) -> ProfessionalResponse:
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    if data.first_name is not None:
        professional.first_name = data.first_name
    if data.last_name is not None:
        professional.last_name = data.last_name
    if data.location is not None:
        location = db.query(Location).filter(Location.city_name == data.location).first()
        if location:
            professional.location_id = location.id
        else:
            raise HTTPException(status_code=404, detail="Location not found")
    if data.phone is not None:
        professional.phone = data.phone
    if data.email is not None:
        professional.email = data.email
    if data.website is not None:
        professional.website = data.website
    if data.summary is not None:
        professional.summary = data.summary
    if data.status is not None:
        professional.status = data.status
    if data.picture is not None:
        professional.picture = data.picture

    db.commit()
    db.refresh(professional)
    return ProfessionalResponse.from_orm(professional)


# WORKS
def get_own_job_applications(db: Session, current_user: User):
    applications = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).all()

    return [
        JobApplicationResponse(
            user_id=app.user_id,
            id=app.id,
            description=app.description,
            min_salary=app.min_salary,
            max_salary=app.max_salary,
            status=app.status,
            location_name=app.location.city_name if app.location else None,
            skills=[
                SkillResponse(
                    skill_id=s.skill.id,
                    name=s.skill.name,
                    level=s.level
                )
                for s in app.skills
            ]
        )
        for app in applications
    ]

