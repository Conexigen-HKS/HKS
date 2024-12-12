"""
This module contains the API routes for job applications.
Routes:
- Create job application
- View job application
- View job applications
- Edit job application
- Delete job application
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.schemas.job_application import (
    JobApplicationEdit,
    JobApplicationResponse,
    JobApplicationCreate,
)
from app.common.auth import get_current_user

from app.data.database import get_db
from app.data.models import User
from app.data.schemas.skills import SkillResponse
from app.services.job_app_service import (
    create_job_application,
    delete_job_application,
    edit_job_app,
    view_job_application,
)
from app.services.professional_service import (
    get_own_job_applications,
    get_professional_by_user_id,
)

job_app_router = APIRouter(tags=["Job Applications"], prefix="/api/job_applications")


@job_app_router.post("/", response_model=JobApplicationResponse)
def create_job_application_(
    data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a job application
    Args:
    - data: JobApplicationCreate
    - db: Session = Depends(get_db)
    - current_user: User = Depends(get_current_user)
    Returns:
    - JobApplicationResponse
    """
    professional = get_professional_by_user_id(db, current_user.id)
    job_application = create_job_application(
        db=db,
        professional_id=str(professional.id),
        user_id=str(current_user.id),
        description=data.description,
        min_salary=data.min_salary,
        max_salary=data.max_salary,
        city_name=data.city_name,
        status=data.status,
        skills=data.skills,
    )

    return JobApplicationResponse(
        user_id=current_user.id,
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=job_application.location.city_name
        if job_application.location
        else None,
        skills=[
            SkillResponse(skill_id=s.skills_id, name=s.skill.name, level=s.level)
            for s in job_application.skills
        ],
    )


@job_app_router.get(
    "/job-applications/{job_application_id}", response_model=JobApplicationResponse
)
def view_application(
    job_application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    View a job application route
    Args:
    - job_application_id: UUID
    - current_user: User = Depends(get_current_user)
    - db: Session = Depends(get_db)
    Returns:
    - JobApplicationResponse
    """
    return view_job_application(
        db=db, job_application_id=job_application_id, user_id=current_user.id
    )


@job_app_router.get("/job-applications", response_model=List[JobApplicationResponse])
def view_job_applications(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    View all job applications route
    Args:
    - current_user: User = Depends(get_current_user)
    - db: Session = Depends(get_db)
    Returns:
    - List[JobApplicationResponse]
    """
    return get_own_job_applications(db, current_user)


@job_app_router.put("/{id}")
def edit_job_app_(
    id: UUID,
    job_app_info: JobApplicationEdit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Edit a job application route
    Args:
    - id: UUID
    - job_app_info: JobApplicationEdit
    - db: Session = Depends(get_db)
    - current_user: User = Depends(get_current_user)
    Returns:
    - JobApplicationResponse
    """
    return edit_job_app(
        job_application_id=id,
        job_app_info=job_app_info,
        db=db,
        current_user=current_user,
    )


@job_app_router.delete("/{id}")
def delete_job_app(
    job_app_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a job application route
    Args:
    - job_app_id: UUID
    - db: Session = Depends(get_db)
    - current_user: User = Depends(get_current_user)
    Returns:
    - None
    """
    return delete_job_application(
        job_application_id=job_app_id, db=db, current_user=current_user
    )
