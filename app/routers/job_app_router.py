from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.schemas.job_application import JobApplicationEdit, JobApplicationResponse, JobApplicationCreate
from app.common.auth import get_current_user

from app.data.database import get_db
from app.data.models import Location, ProfessionalProfile, User
from app.services.job_app_service import create_job_application, delete_job_application, get_job_application, get_all_job_applications_service, edit_job_app
from app.services.professional_service import get_professional_by_user_id

job_app_router = APIRouter(tags=["Job Applications"], prefix="/api/job_applications")

#WORKS
@job_app_router.post("/", response_model=JobApplicationResponse)
def create_job_application_(
    data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
        skills=data.skills
    )

    return JobApplicationResponse(
        user_id=current_user.id,  # Added user_id here
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=job_application.location.city_name if job_application.location else None,
        skills=[s.skill.name for s in job_application.skills]
    )

#WORKS
@job_app_router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_job_application_(
    job_application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    professional = get_professional_by_user_id(db, current_user.id)

    profile, match_requests = get_job_application(db, job_application_id)

    if profile.professional_id != professional.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job application")

    location_name = None
    if profile.location_id:
        location = db.query(Location).filter(Location.id == profile.location_id).first()
        location_name = location.city_name if location else None

    return JobApplicationResponse(
        user_id=current_user.id,  # Added user_id here
        id=profile.id,
        description=profile.description,    
        min_salary=profile.min_salary,
        max_salary=profile.max_salary,
        location_name=location_name,
        status=profile.status,
        skills=[s.skill.name for s in profile.skills]
    )


#WORKS
@job_app_router.get("/", response_model=List[JobApplicationResponse])
def get_all_job_applications(
    db: Session = Depends(get_db),
    current_user: ProfessionalProfile = Depends(get_current_user)
):
    if not current_user.professional:
        raise HTTPException(status_code=404, detail="Professional application not found for current user.")
    
    professional_id = current_user.professional.id
    applications = get_all_job_applications_service(db, professional_id)
    return applications

@job_app_router.put("/{id}")
def edit_job_app_(
    id: UUID,
    job_app_info: JobApplicationEdit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return edit_job_app(
        job_application_id=id,
        job_app_info=job_app_info,
        db=db,
        current_user=current_user
    )

@job_app_router.delete("/{id}")
def delete_job_app(
    job_app_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    return delete_job_application(
        job_application_id=job_app_id,
        db=db,
        current_user=current_user)