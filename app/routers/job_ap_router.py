from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.schemas.job_application import JobApplicationResponse, JobApplicationCreate
from app.common.auth import get_current_user

from app.data.database import get_db
from app.data.models import Professional, Location, User, ProfessionalProfileSkills, Skills
from app.services.jop_ap_service import create_job_application, get_job_application, set_main_job_application_service, get_all_job_applications_service, search_job_ads_service
from app.services.professional_service import get_professional_by_user_id

job_app_router = APIRouter(tags=["Job Applications"], prefix="/job_applications")

@job_app_router.post("/", response_model=JobApplicationResponse)
def create_job_application_endpoint(
        data: JobApplicationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    professional = get_professional_by_user_id(db, current_user.id)

    location_id = data.location_id
    if not location_id and data.location_name:
        location = db.query(Location).filter(Location.city_name == data.location_name).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        location_id = location.id

    job_application = create_job_application(
        db=db,
        professional_id=professional.id,
        user_id=current_user.id,
        description=data.description,
        min_salary=data.min_salary,
        max_salary=data.max_salary,
        location_id=location_id,
        status=data.status,
        skills=data.skills
    )

    return JobApplicationResponse(
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=data.location_name if data.location_name else None,
        skills=[skill.name for skill in db.query(Skills).join(
            ProfessionalProfileSkills, ProfessionalProfileSkills.skills_id == Skills.id
        ).filter(ProfessionalProfileSkills.professional_profile_id == job_application.id).all()]
    )

@job_app_router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_job_application_endpoint(
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
        id=profile.id,
        description=profile.description,
        min_salary=profile.min_salary,
        max_salary=profile.max_salary,
        location_name=location_name,
        status=profile.status,
        skills=[s.skill.name for s in profile.skills]
    )

@job_app_router.patch("/{job_application_id}/set-main")
def set_main_job_application(job_application_id: UUID, db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user)):
    application = set_main_job_application_service(db, job_application_id, current_user.id)
    return {"message": "Main application set successfully", "application_id": application.id}


@job_app_router.get("/", response_model=List[JobApplicationResponse])
def get_all_job_applications(db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user)):
    applications = get_all_job_applications_service(db, current_user.id)
    return applications
