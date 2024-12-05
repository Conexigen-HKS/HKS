from typing import List, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.professional import ProfessionalUpdate, ProfessionalResponse
from app.data.schemas.job_application import JobApplicationResponse
from app.services.company_service import find_all_companies_service
from app.services.job_app_service import (
    set_main_job_application_service, 
    search_job_ads_service
)
from app.services.match_service import view_matches
from app.services.professional_service import (
    view_own_profile,
    update_own_profile)

professional_router = APIRouter(
    prefix="/professionals", 
    tags=["Professionals"]
)

#WORKS
@professional_router.get("/profile", response_model=ProfessionalResponse)
def view_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return view_own_profile(db, current_user.id)

#WORKS
@professional_router.patch("/profile", response_model=ProfessionalResponse)
def edit_profile(
    data: ProfessionalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_own_profile(db, current_user.id, data)

#WORKS
@professional_router.patch("/job-applications/{job_application_id}/set-main")
def set_main_application(
    job_application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return set_main_job_application_service(db=db,job_application_id=job_application_id,current_user=current_user)


#WORKS
@professional_router.get("/search-job-ads", response_model=List[JobApplicationResponse])
def search_job_ads(
    query: Optional[str] = Query(None, description="Search term to filter job ads by description"),
    location: Optional[str] = Query(None, description="City or location to filter job ads"),
    min_salary: Optional[int] = Query(None, description="Filter job ads with minimum salary greater than or equal to this value"),
    max_salary: Optional[int] = Query(None, description="Filter job ads with maximum salary less than or equal to this value"),
    order_by: Literal["asc", "desc"] = Query("asc", description="Sort order for job ads based on minimum salary"),
    db: Session = Depends(get_db)
):

    return search_job_ads_service(
        db=db,
        query=query,
        location=location,
        min_salary=min_salary,
        max_salary=max_salary,
        order_by=order_by
    )

#WORKS
@professional_router.get("/companies-list")
def get_all_companies(
    db: Session = Depends(get_db)
):
    companies = find_all_companies_service(db=db)
    return companies

#WORKS
@professional_router.get("/matches")
def get_all_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return view_matches(db=db,current_user=current_user)