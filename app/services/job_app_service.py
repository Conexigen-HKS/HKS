"""
This module contains the service functions for the job application endpoints.
Methods:
    - create_job_application
    - get_job_application
    - set_main_job_application_service
    - get_all_job_applications_service
    - search_job_ads_service
    - get_archived_job_applications_service
    - search_job_applications_service
    - view_job_application
    - edit_job_app
    - delete_job_application
    - get_recent_applications
    - get_spotlight_application
"""

from typing import List, Literal, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.data.models import (
    CompanyOffers,
    Location,
    Professional,
    ProfessionalProfile,
    ProfessionalProfileSkills,
    RequestsAndMatches,
    Skills,
    User,
)
from app.data.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationEdit,
    JobApplicationResponse,
)
from app.data.schemas.skills import SkillResponse


# WORKS
def create_job_application(db: Session, user_id: UUID, job_data: JobApplicationCreate):
    """
    Create a new job application for a professional.
    Args:
        description (str): The job application description.
        min_salary (int): The minimum salary expectation.
        max_salary (int): The maximum salary expectation.
        status (str): The status of the job application.
        city_name (str): The name of the city where the job is located.
        skills (List[SkillResponse]): A list of skills and their levels.
        Returns:
        JobApplicationResponse: The created job application.
    """
    description = job_data.description
    min_salary = job_data.min_salary
    max_salary = job_data.max_salary
    status = job_data.status
    city_name = job_data.city_name
    skills = job_data.skills

    # Handle location creation or fetching
    location = db.query(Location).filter_by(city_name=city_name).first()
    if not location:
        location = Location(city_name=city_name)
        db.add(location)
        db.commit()
        db.refresh(location)

    # Create professional profile
    professional = db.query(Professional).filter_by(user_id=user_id).first()
    profile = ProfessionalProfile(
        user_id=user_id,
        professional_id=professional.id,
        description=description,
        min_salary=min_salary,
        max_salary=max_salary,
        status=status,
        location_id=location.id,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Associate skills with levels
    for skill_data in skills:
        skill = db.query(Skills).filter(Skills.name == skill_data.name).first()
        if not skill:
            skill = Skills(name=skill_data.name)
            db.add(skill)
            db.commit()
            db.refresh(skill)

        skill_assignment = ProfessionalProfileSkills(
            professional_profile_id=profile.id,
            skills_id=skill.id,
            level=skill_data.level,
        )
        db.add(skill_assignment)

    db.commit()


def get_job_application(db: Session, job_application_id: UUID):
    """
    Get a job application by its ID.
    Args:
    job_application_id (UUID): The ID of the job application.
    Returns:
    JobApplicationResponse: The job application.
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


# WORKS
def set_main_job_application_service(
    db: Session, job_application_id: str, current_user: User
):
    """
    Set the main job application for a professional.
    Args:
    job_application_id (str): The ID of the job application.
    current_user (User): The current user.
    Returns:
    HTTPException: The HTTP response.
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
    Get all job applications for a professional.
    Args:
    professional_id (UUID): The ID of the professional.
    Returns:
    List[JobApplicationResponse]: A list of job applications.
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
    Search for job ads based on the provided filters.
    Args:
    query (str): The search query.
    location (str): The location to filter by.
    min_salary (int): The minimum salary to filter by.
    max_salary (int): The maximum salary to filter by.
    """
    if min_salary and max_salary and min_salary > max_salary:
        raise ValueError("Minimum salary cannot be higher than maximum salary")

    job_ads_query = db.query(CompanyOffers).filter(CompanyOffers.status == "Active")

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
        {
            "id": ad.id,
            "title": ad.title,
            "company_name": ad.company.name,
            "description": ad.description,
            "min_salary": ad.min_salary,
            "max_salary": ad.max_salary,
            "location_name": ad.location.city_name if ad.location else None,
            "status": ad.status,
        }
        for ad in job_ads
    ]


def get_archived_job_applications_service(db: Session):
    """
    Get all archived job applications.
    Args:
    db (Session): The database session.
    Returns:
    List[JobApplicationResponse]: A list of job applications.
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
    Search for job applications based on the provided filters.
    Args:
    query (str): The search query.
    location (str): The location to filter by.
    skill (str): The skill to filter by.
    Returns:
    List[JobApplicationResponse]: A list of job applications.
    """
    job_applications_query = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.status == "Active"
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
    View a job application by its ID.
    Args:
    job_application_id (UUID): The ID of the job application.
    user_id (UUID): The ID of the user.
    Returns:
    JobApplicationResponse: The job application.
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
    Edit a job application.
    Args:
    job_application_id (UUID): The ID of the job application.
    job_app_info (JobApplicationEdit): The job application data.
    db (Session): The database session.
    current_user (User): The current user.
    Returns:
    JobApplicationResponse: The edited job application.
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
    Delete a job application.
    Args:
    job_application_id (UUID): The ID of the job application.
    db (Session): The database session.
    current_user (User): The current user.
    Returns:
    dict: The response message.
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


def get_recent_applications(db: Session, limit: int = 3):
    """
    Get a list of recent job applications.
    Args:
    db (Session): The database session.
    limit (int): The number of applications to return.
    Returns:
    List[dict]: A list of job applications.
    """
    applications = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.status == "Active"
        )  # Filter for Active applications
        .options(
            joinedload(ProfessionalProfile.location),
            joinedload(ProfessionalProfile.skills).joinedload(
                ProfessionalProfileSkills.skill
            ),
            joinedload(
                ProfessionalProfile.professional
            ),  # Load the related professional
        )
        .order_by(func.random())  # Randomize results
        .limit(limit)
        .all()
    )

    # Format the applications for readability
    return [
        {
            "id": app.id,
            "first_name": app.professional.first_name,
            "last_name": app.professional.last_name,
            "description": app.description,
            "location_name": app.location.city_name if app.location else "N/A",
            "skills": [skill.skill.name for skill in app.skills],  # Extract skill names
            "min_salary": app.min_salary,
            "max_salary": app.max_salary,
            "status": app.status,
            "picture": app.professional.picture or "/static/images/default-profile.png",
        }
        for app in applications
    ]


def get_spotlight_application(db: Session):
    """
    Get a spotlight job application.
    Args:
    db (Session): The database session.
    Returns:
    dict: The spotlight job application.
    """
    application = (
        db.query(ProfessionalProfile)
        .filter(
            ProfessionalProfile.status == "Active"
        )  # Filter for Active applications
        .options(
            joinedload(ProfessionalProfile.professional),  # Load professional's details
            joinedload(ProfessionalProfile.skills).joinedload(
                ProfessionalProfileSkills.skill
            ),  # Load skills
        )
        .order_by(func.random())
        .first()
    )

    if not application:
        return None

    return {
        "first_name": application.professional.first_name,
        "last_name": application.professional.last_name,
        "job_title": application.description,
        "skills": [skill.skill.name for skill in application.skills],
        "min_salary": application.min_salary,
        "max_salary": application.max_salary,
        "summary": application.description or "",
    }
