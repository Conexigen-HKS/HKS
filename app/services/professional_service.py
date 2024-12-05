"""
Professional service module
In this module, we define the professional service functions. We have the following functions:
- get_professional_by_user_id: This function is used to get a professional by user ID.
- get_professional_service: This function is used to get a professional.
- update_professional_service: This function is used to update a professional.
- update_professional_status_on_match: This function is used to update the professional status on match.
- create_professional_application: This function is used to create a professional application.
- get_professional_profile_for_user: This function is used to get a professional profile for a user.
- view_own_profile: This function is used to view own profile.
- update_own_profile: This function is used to update own profile.
- get_own_job_applications: This function is used to get own job applications.
"""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.models import (
    User,
    ProfessionalProfile,
    CompanyOffers,
    Professional,
    RequestsAndMatches,
    Location,
)
from app.data.schemas.job_application import JobApplicationResponse
from app.data.schemas.professional import ProfessionalUpdate, ProfessionalResponse
from app.data.schemas.skills import SkillResponse


def get_professional_by_user_id(db: Session, user_id: UUID):
    """
    Get a professional by user ID
    :param db: Database session
    :param user_id: User ID
    :return: Professional
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return professional


def get_professional_service(db: Session, user_id: UUID):
    """
    Get a professional
    :param db: Database session
    :param user_id: User ID
    :return: Professional
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return professional


def update_professional_service(
    db: Session, user_id: UUID, update_data: ProfessionalUpdate
):
    """
    Update a professional
    :param db: Database session
    :param user_id: User ID
    :param update_data: Professional update data
    :return: Professional
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(professional, key, value)

    db.commit()
    db.refresh(professional)
    return professional


def update_professional_status_on_match(db: Session, professional_profile_id: UUID):
    """
    Update the professional status on match
    :param db: Database session
    :param professional_profile_id: Professional profile ID
    :return: Professional profile
    """
    profile = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.id == professional_profile_id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    has_matches = (
        db.query(RequestsAndMatches)
        .filter(RequestsAndMatches.professional_profile_id == professional_profile_id)
        .count()
    )

    if has_matches > 0:
        profile.status = "busy"
    else:
        profile.status = "active"

    db.commit()
    return profile


def create_professional_application(
    db: Session,
    professional_profile_id: str,
    min_salary: int,
    max_salary: int,
    location: str,
    description: str,
):
    """
    Create a professional application
    :param db: Database session
    :param professional_profile_id: Professional profile ID
    :param min_salary: Minimum salary
    :param max_salary: Maximum salary
    :param location: Location
    :param description: Description
    :return: Professional application
    """
    professional_application = CompanyOffers(
        professional_profile_id=professional_profile_id,
        type="professional",
        status="active",
        min_salary=min_salary,
        max_salary=max_salary,
        location=location,
        description=description,
    )
    db.add(professional_application)
    db.commit()
    db.refresh(professional_application)
    return professional_application


def get_professional_profile_for_user(db: Session, user_id: str):
    """
    Get a professional profile for a user
    :param db: Database session
    :param user_id: User ID
    :return: Professional profile
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    professional_profile = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.professional_id == professional.id)
        .first()
    )
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    return professional_profile


def view_own_profile(db: Session, user_id: UUID):
    """
    View own profile
    :param db: Database session
    :param user_id: User ID
    :return: Professional profile
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return ProfessionalResponse.from_orm(professional)


def update_own_profile(
    db: Session, user_id: UUID, data: ProfessionalUpdate
) -> ProfessionalResponse:
    """
    Update own profile
    :param db: Database session
    :param user_id: User ID
    :param data: Professional update data
    :return: Professional profile
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == user_id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    if data.first_name is not None:
        professional.first_name = data.first_name
    if data.last_name is not None:
        professional.last_name = data.last_name
    if data.location is not None:
        location = (
            db.query(Location).filter(Location.city_name == data.location).first()
        )
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


def get_own_job_applications(db: Session, current_user: User):
    """
    Get own job applications
    :param db: Database session
    :param current_user: Current user
    :return: List of job applications
    """
    applications = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.user_id == current_user.id)
        .all()
    )

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
                SkillResponse(skill_id=s.skill.id, name=s.skill.name, level=s.level)
                for s in app.skills
            ],
        )
        for app in applications
    ]
