"""
This module contains the API routes for the company endpoints.
Methods:
    - show_company_description: GET /companies/info
    - edit_company_description: PUT /companies/info
    - show_all_companies: GET /companies/all
    - search_or_get_job_applications: GET /companies/job-applications
    - get_all_professionals_: GET /companies/professionals-list
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.common import auth
from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.company import ShowCompanyModel, CompanyInfoRequestModel
from app.data.schemas.job_application import JobApplicationResponse
from app.services.offer_service import send_offer_request
from app.services.company_service import (
    edit_company_description_service,
    find_all_companies_service,
    get_all_professionals,
    show_company_description_service,
)
from app.services.job_app_service import search_job_applications_service


company_router = APIRouter(prefix="/api/companies", tags=["Companies"])


@company_router.get("/info", response_model=List[ShowCompanyModel])
def show_company_description(
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    """
    This function returns the company description of the current user.
    :param current_user: User
    :param db: Session
    :return: List[ShowCompanyModel]
    """
    show_company = show_company_description_service(user=current_user, db=db)

    if show_company:
        return [show_company]
    else:
        raise HTTPException(
            status_code=400,
        )


@company_router.put('/info')
def edit_company_description(
    company_info: CompanyInfoRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    This function updates the company description of the current user.
    :param company_info: CompanyInfoRequestModel
    :param current_user: User
    :param db: Session
    :return: Dict
    """
    company_username = current_user.username

    if not company_username:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"

        )
    updated_company = edit_company_description_service(company_info, company_username, db=db)

    if updated_company:
        return {"message": "Company description updated successfully", "company": updated_company}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while updating the company description"
        )


@company_router.get('/all')
def show_all_companies(db: Session = Depends(get_db)):
    """
    This function returns all companies in the database.
    :param db: Session
    :return: List[ShowCompanyModel]
    """
    companies = find_all_companies_service(db=db)
    return companies


@company_router.get("/job-applications", response_model=List[JobApplicationResponse])
def search_or_get_job_applications(
        query: Optional[str] = Query(None),
        location: Optional[str] = Query(None),
        skill: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """
    This function returns the job applications based on the query, location, and skill.
    :param query: Optional[str]
    :param location: Optional[str]
    :param skill: Optional[str]
    :param db: Session
    :param current_user: User
    :return: List[JobApplicationResponse]
    """
    if current_user.role != 'company':
        raise HTTPException(status_code=403, detail="Only companies can access this endpoint")

    return search_job_applications_service(db, query, location, skill)


@company_router.get("/professionals-list")
def get_all_professionals_(db: Session = Depends(get_db)):
    """
    This function returns all professionals in the database.
    :param db: Session
    :return: List[User]
    """
    return get_all_professionals(db=db)

@company_router.post("/send_offer")
def send_offer(
    target_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return send_offer_request(db, professional_profile_id=target_id, current_user=current_user)
