"""
Job application service module.
In this file, we define the job application service. We have the following functions:
- create_job_application: This function is used to create a job application.
- get_job_application: This function is used to get a job application.
- set_main_job_application_service: This function is used to set the main job application.
- get_all_job_applications_service: This function is used to get all job applications.
- search_job_ads_service: This function is used to search job ads.
- get_archived_job_applications_service: This function is used to get archived job applications.
- search_job_applications_service: This function is used to search job applications.
- view_job_application: This function is used to view a job application.
- edit_job_app: This function is used to edit a job application.
- delete_job_application: This function is used to delete a job application.
"""

from typing import List, Literal, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.data.models import (
    Professional,
    ProfessionalProfile,
    ProfessionalProfileSkills,
    Skills,
    RequestsAndMatches,
    CompanyOffers,
    Location,
    User,
)
from app.data.schemas.job_application import JobApplicationEdit, JobApplicationResponse
from app.data.schemas.skills import SkillCreate, SkillResponse

# TODO - Add functionality to allow adding new skills/requirements and consider an approval workflow.

# NOTE - Status
# Active – the Job application is visible in searches by the Company
# Hidden – the Job application is not visible for anyone but the creator
# Private – the Job application can be viewed by id, but do not appear in searches should
# Matched – when is matched by a company


def create_job_application(
    db: Session,
    professional_id: str,
    user_id: str,
    description: str,
    min_salary: int,
    max_salary: int,
    city_name: str,
    status: str,
    skills: List[SkillCreate],
):
    """
    Create a job application
    Accepts a database session, a professional id, a user id, a description,
    a minimum salary, a maximum salary, a city name, a status,
    and a list of skills and returns a job application.
    """
    location = db.query(Location).filter(Location.city_name == city_name).first()
    if not location:
        raise HTTPException(
            status_code=400, detail=f"Location '{city_name}' does not exist."
        )

    job_application = ProfessionalProfile(
        professional_id=professional_id,
        user_id=user_id,
        description=description,
        min_salary=min_salary,
        max_salary=max_salary,
        location_id=location.id,
        status=status,
    )
    db.add(job_application)
    db.commit()
    db.refresh(job_application)

    for skill_data in skills:
        skill = db.query(Skills).filter(Skills.name == skill_data.name).first()
        if not skill:
            skill = Skills(name=skill_data.name)
            db.add(skill)
            db.commit()
            db.refresh(skill)

        skill_assignment = ProfessionalProfileSkills(
            professional_profile_id=job_application.id,
            skills_id=skill.id,
            level=skill_data.level or None,
        )
        db.add(skill_assignment)

    db.commit()
    return job_application


def get_job_application(db: Session, job_application_id: UUID):
    """
    Get a job application
    Accepts a database session and a job application id and returns a job application.
    """
    profile = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.id == job_application_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Job application not found")

    matches = (
        db.query(RequestsAndMatches.company_offers_id)
        .filter(RequestsAndMatches.professional_profile_id == job_application_id)
        .all()
    )
    return profile, [match.company_offers_id for match in matches]


def set_main_job_application_service(
    db: Session, job_application_id: str, current_user: User
):
    """
    Set the main job application
    Accepts a database session, a job application id, and a current user object
    and sets the main job application.
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == current_user.id).first()
    )

    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    application = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.id == job_application_id,
            ProfessionalProfile.professional_id == professional.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="ProfessionalProfile not found")

    db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional.id
    ).update({"status": "Hidden"}, synchronize_session="fetch")

    application.status = "Active"
    db.commit()

    return HTTPException(status_code=200, detail="Main application set successfully")


def get_all_job_applications_service(
    db: Session, professional_id: UUID
) -> List[JobApplicationResponse]:
    """
    Get all job applications
    Accepts a database session and a professional id and returns a list of job applications.
    """
    applications = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.professional_id == professional_id)
        .all()
    )

    return [
        {
            "user_id": app.professional_id,
            "id": app.id,
            "description": app.description,
            "min_salary": app.min_salary,
            "max_salary": app.max_salary,
            "status": app.status,
            "location_name": app.location.city_name if app.location else None,
            "skills": [s.skill.name for s in app.skills],
        }
        for app in applications
    ]


def search_job_ads_service(
    db: Session,
    query: Optional[str] = None,
    location: Optional[str] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    order_by: Literal["asc", "desc"] = "asc",
):
    """
    Search job ads
    Accepts a database session, a query, a location, a minimum salary, a maximum salary,
    and an order by and returns a list of job applications.
    """
    if min_salary and max_salary and min_salary > max_salary:
        raise ValueError("Minimum salary cannot be higher than maximum salary")

    job_ads_query = db.query(CompanyOffers).filter(CompanyOffers.status == "active")

    if query:
        job_ads_query = job_ads_query.filter(
            CompanyOffers.description.ilike(f"%{query}%")
        )

    if location:
        job_ads_query = job_ads_query.join(Location).filter(
            Location.city_name.ilike(f"%{location}%")
        )

    if min_salary:
        job_ads_query = job_ads_query.filter(CompanyOffers.min_salary >= min_salary)

    if max_salary:
        job_ads_query = job_ads_query.filter(CompanyOffers.max_salary <= max_salary)

    if order_by == "desc":
        job_ads_query = job_ads_query.order_by(CompanyOffers.min_salary.desc())
    else:
        job_ads_query = job_ads_query.order_by(CompanyOffers.min_salary.asc())

    job_ads = job_ads_query.options(joinedload(CompanyOffers.location)).all()

    return [
        JobApplicationResponse(
            user_id=ad.company.user_id,
            id=ad.id,
            description=ad.description,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            status=ad.status,
            location_name=ad.location.city_name if ad.location else None,
            skills=[],
        )
        for ad in job_ads
    ]


def get_archived_job_applications_service(db: Session):
    """
    Get archived job applications
    Accepts a database session and returns a list of archived job applications.
    """
    archived_job_apps = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.status == "Matched")
        .all()
    )

    return [
        JobApplicationResponse(
            id=job_app.id,
            description=job_app.description,
            min_salary=job_app.min_salary,
            max_salary=job_app.max_salary,
            status=job_app.status,
            location_name=job_app.location.city_name if job_app.location else "N/A",
            skills=[skill.skill.name for skill in job_app.skills],
        )
        for job_app in archived_job_apps
    ]


def search_job_applications_service(
    db: Session,
    query: Optional[str] = None,
    location: Optional[str] = None,
    skill: Optional[str] = None,
):
    """
    Search job applications
    Accepts a database session, a query, a location, and a skill and returns a list of job applications.
    """
    job_applications_query = db.query(ProfessionalProfile).filter(
    func.lower(ProfessionalProfile.status) == "active"
    )

    if query:
        job_applications_query = job_applications_query.filter(
            ProfessionalProfile.description.ilike(f"%{query}%")
        )

    if location:
        job_applications_query = job_applications_query.join(Location).filter(
            Location.city_name.ilike(f"%{location}%")
        )

    if skill:
        job_applications_query = (
            job_applications_query.join(ProfessionalProfile.skills)
            .join(Skills)
            .filter(Skills.name.ilike(f"%{skill}%"))
        )

    job_apps = job_applications_query.all()

    return [
        JobApplicationResponse(
            user_id=job_app.user_id,
            id=job_app.id,
            description=job_app.description,
            min_salary=job_app.min_salary,
            max_salary=job_app.max_salary,
            status=job_app.status,
            location_name=job_app.location.city_name if job_app.location else "N/A",
            skills=[
                SkillResponse(skill_id=s.skill.id, name=s.skill.name, level=s.level)
                for s in job_app.skills
            ],
        )
        for job_app in job_apps
    ]


def view_job_application(db: Session, job_application_id: UUID, user_id: UUID):
    """
    View a job application
    Accepts a database session, a job application id, and a user id and returns a job application.
    """
    job_application = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.id == job_application_id,
            ProfessionalProfile.user_id == user_id,
        )
        .first()
    )
    if not job_application:
        raise HTTPException(status_code=404, detail="Job application not found")

    return JobApplicationResponse(
        user_id=job_application.user_id,
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=job_application.location.city_name
        if job_application.location
        else None,
        skills=[
            SkillResponse(skill_id=s.skill.id, name=s.skill.name, level=s.level)
            for s in job_application.skills
        ],
    )


def edit_job_app(
    job_application_id: UUID,
    job_app_info: JobApplicationEdit,
    db: Session,
    current_user: User,
):
    """
    Edit a job application
    Accepts a job application id, a job application info, a database session,
    and a current user object and returns the edited job application.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    professional_app = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.id == job_application_id,
            ProfessionalProfile.user_id == user.id,
        )
        .first()
    )
    if not professional_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    if job_app_info.location:
        location = (
            db.query(Location)
            .filter(Location.city_name == job_app_info.location)
            .first()
        )
        if not location:
            raise HTTPException(
                status_code=400, detail=f"Location '{job_app_info.location}' not found."
            )
        professional_app.location_id = location.id

    if job_app_info.description is not None:
        professional_app.description = job_app_info.description
    if job_app_info.min_salary is not None:
        professional_app.min_salary = job_app_info.min_salary
    if job_app_info.max_salary is not None:
        professional_app.max_salary = job_app_info.max_salary
    if job_app_info.status is not None:
        professional_app.status = job_app_info.status

    if job_app_info.skills is not None:
        professional_app.skills.clear()
        for skill_data in job_app_info.skills:
            skill = db.query(Skills).filter(Skills.name == skill_data.name).first()
            if not skill:
                skill = Skills(name=skill_data.name)
                db.add(skill)
                db.commit()
                db.refresh(skill)
            skill_assignment = ProfessionalProfileSkills(
                professional_profile_id=professional_app.id,
                skills_id=skill.id,
                level=skill_data.level,
            )
            db.add(skill_assignment)

    db.commit()
    db.refresh(professional_app)

    return {
        "description": professional_app.description,
        "min_salary": professional_app.min_salary,
        "max_salary": professional_app.max_salary,
        "status": professional_app.status,
        "location": professional_app.location.city_name
        if professional_app.location
        else "N/A",
        "skills": [s.skill.name for s in professional_app.skills],
    }


def delete_job_application(job_application_id: UUID, db: Session, current_user: User):
    """
    Delete a job application
    Accepts a job application id, a database session, and a current user object
    and returns a message.
    """
    professional = (
        db.query(Professional).filter(Professional.user_id == current_user.id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    app_to_delete = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.id == job_application_id,
            ProfessionalProfile.professional_id == professional.id,
        )
        .first()
    )

    if not app_to_delete:
        raise HTTPException(status_code=404, detail="Application not found.")
    db.delete(app_to_delete)
    db.commit()

    return {"detail": "Application deleted successfully"}
