from typing import Optional
from uuid import UUID
from venv import logger

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from HKS.data.schemas.job_application import JobApplicationResponse, JobApplicationCreate
from app.common.auth import get_current_user
from app.services.job_application_service import get_job_application, assign_skill_to_job_application_by_name, \
    create_job_application

from HKS.data.database import get_db
from HKS.data.models import ProfessionalProfile, Professional, Locations

job_app_router = APIRouter(tags=["Job Applications"], prefix="/job_applications")

@job_app_router.post("/", response_model=JobApplicationResponse)
def create_job_application_endpoint(data: JobApplicationCreate, db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user) ):
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Only professionals can create job applications")

    professional = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    location_id = data.location_id
    if not location_id and data.location_name:
        location = db.query(Locations).filter(Locations.name == data.location_name).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        location_id = location.id

    job_application = create_job_application(
        db=db,
        professional_id=professional.id,
        min_salary=data.min_salary,
        max_salary=data.max_salary,
        location_id=location_id,
        description=data.description
    )

    return JobApplicationResponse(
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=data.location_name if data.location_name else None,
        skills=[]
    )

@job_app_router.post("/{job_application_id}/skills-by-name")
def assign_skill_by_name_to_job_application_endpoint(job_application_id: UUID, skill_name: str, level: Optional[int] = None, db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user)):
    professional_profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == job_application_id
    ).first()

    if not professional_profile or professional_profile.professional_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this job application")

    assigned_skill = assign_skill_to_job_application_by_name(db, job_application_id, skill_name, level)
    return {
        "message": "Skill assigned successfully",
        "skill_name": skill_name,
        "level": level
    }

@job_app_router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_job_application_endpoint(job_application_id: UUID, db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user)):
    profile, match_requests = get_job_application(db, job_application_id)

    if profile.professional_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job application")

    location_name = None
    if profile.location_id:
        location = db.query(Locations).filter(Locations.id == profile.location_id).first()
        location_name = location.name if location else None

    return JobApplicationResponse(
        id=profile.id,
        description=profile.description,
        min_salary=profile.min_salary,
        max_salary=profile.max_salary,
        location_name=location_name,
        status=profile.status,
        skills=[s.skill.name for s in profile.skills]
    )