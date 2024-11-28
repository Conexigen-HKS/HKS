from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.professional import ProfessionalUpdate, ProfessionalResponse
from app.data.schemas.job_application import JobApplicationResponse, JobApplicationCreate
from app.services.jop_ap_service import set_main_job_application_service, create_job_application, view_job_application, \
    search_job_ads_service
from app.services.professional_service import (
    view_own_profile,
    update_own_profile,
    get_own_job_applications)

professional_router = APIRouter(prefix="/professionals", tags=["Professionals"])


@professional_router.get("/profile", response_model=ProfessionalResponse)
def view_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return view_own_profile(db, current_user.id)

#WORKS - changed http method to patch. Prev was put.
@professional_router.patch("/profile", response_model=ProfessionalResponse)
def edit_profile(
    data: ProfessionalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_own_profile(db, current_user.id, data)


@professional_router.get("/job-applications", response_model=List[JobApplicationResponse])
def view_job_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_own_job_applications(db, current_user.id)


@professional_router.patch("/job-applications/{job_application_id}/set-main")
def set_main_application(
    job_application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return set_main_job_application_service(db, job_application_id, current_user.id)




@professional_router.get("/job-applications/{job_application_id}", response_model=JobApplicationResponse)
def view_application(
    job_application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return view_job_application(db, job_application_id, current_user.id)




@professional_router.get("/search-job-ads", response_model=List[JobApplicationResponse])
def search_job_ads(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return search_job_ads_service(db, query, location)
