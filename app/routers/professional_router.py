"""
This module contains the API routes for the professional user.
In this file, we define the routes for the professional user service.
We have the following endpoints:
- view_profile: This endpoint is used to view the profile of a professional user.
- edit_profile: This endpoint is used to edit the profile of a professional user.
- set_main_application:
  This endpoint is used to set the main job application for a professional user.
- search_job_ads: This endpoint is used to search for job ads.
- get_all_companies: This endpoint is used to get a list of all companies.
- get_all_matches: This endpoint is used to get all matches for a professional user.
"""
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
    search_job_ads_service,
)
from app.services.match_service import view_matches
from app.services.offer_service import accept_offer, decline_offer
from app.services.professional_service import view_own_profile, update_own_profile

professional_router = APIRouter(prefix="/api/professionals", tags=["Professionals"])


@professional_router.get("/profile", response_model=ProfessionalResponse)
def view_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    View profile
    Accepts a current user object and a database session.
    Returns the profile of the current user.
    """
    return view_own_profile(db, current_user.id)


@professional_router.patch("/profile", response_model=ProfessionalResponse)
def edit_profile(
    data: ProfessionalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit profile
    Accepts a profile update object, a current user object, and a database session.
    Returns the updated profile of the current user.
    """
    return update_own_profile(db, current_user.id, data)


@professional_router.patch("/job-applications/{job_application_id}/set-main")
def set_main_application(
    job_application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set main job application
    Accepts a job application id, a current user object, and a database session.
    Returns the updated job application.
    """
    return set_main_job_application_service(
        db=db, job_application_id=job_application_id, current_user=current_user
    )


@professional_router.get("/search-job-ads", response_model=List[JobApplicationResponse])
def search_job_ads(
    query: Optional[str] = Query(
        None, description="Search term to filter job ads by description"
    ),
    location: Optional[str] = Query(
        None, description="City or location to filter job ads"
    ),
    min_salary: Optional[int] = Query(
        None,
        description="Filter job ads with minimum salary greater than or equal to this value",
    ),
    max_salary: Optional[int] = Query(
        None,
        description="Filter job ads with maximum salary less than or equal to this value",
    ),
    order_by: Literal["asc", "desc"] = Query(
        "asc", description="Sort order for job ads based on minimum salary"
    ),
    db: Session = Depends(get_db),
):
    """
    Search job ads
    Accepts a search query, location, minimum salary, maximum salary, sort order, and a database session.
    Returns a list of job ads that match the search criteria.
    """
    return search_job_ads_service(
        db=db,
        query=query,
        location=location,
        min_salary=min_salary,
        max_salary=max_salary,
        order_by=order_by,
    )


@professional_router.get("/companies-list")
def get_all_companies(db: Session = Depends(get_db)):
    """
    Get all companies
    Accepts a database session.
    Returns a list of all companies
    """
    companies = find_all_companies_service(db=db)
    return companies


@professional_router.get("/matches")
def get_all_matches(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all matches
    Accepts a database session and a current user object.
    Returns a list of all matches for the current user.
    """
    return view_matches(db=db, current_user=current_user)

@professional_router.post("/accept-offer")
def accept_offer_by_id(
    offer_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    return accept_offer(offer_id=offer_id, db=db, current_user=current_user)

@professional_router.post("/decline-offer")
def decline_offer_by_id(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return decline_offer(offer_id=offer_id,db=db,current_user=current_user)