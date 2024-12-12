"""
This module contains the API routes for the company endpoints.
Methods:
    - show_company_description: GET /companies/info
    - edit_company_description: PUT /companies/info
    - show_all_companies: GET /companies/all
    - search_or_get_job_applications: GET /companies/job-applications
    - get_all_professionals_: GET /companies/professionals-list
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session, joinedload
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User, CompanyOffers
from app.data.schemas.company import CompanyInfoRequestModel
from app.services.company_service import (
    edit_company_description_service,
    show_company_description_service,
)

templates = Jinja2Templates(directory="app/templates")


company_router_web = APIRouter(prefix="/companies", tags=["Companies"])


@company_router_web.get("/dashboard", response_class=HTMLResponse)
async def company_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Render the company profile page.
    Accepts a GET request and returns the company profile page.
    """
    company_data = show_company_description_service(current_user, db)

    profile_picture = company_data.get("company_logo") or "/static/images/default-profile.png"
    return templates.TemplateResponse(
        "company_dashboard.html",
        {
            "request": request,
            "company_name": company_data.get("company_name"),
            "company_description": company_data.get("company_description"),
            "location": company_data.get("company_location"),
            "phone": company_data.get("company_phone"),
            "email": company_data.get("company_email"),
            "website": company_data.get("company_website"),
            "profile_picture": profile_picture,
        },
    )


@company_router_web.put('/info')
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


@company_router_web.get("/offers", response_class=HTMLResponse)
async def view_company_job_offers(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    View all job offers for the company.
    Accepts a GET request and returns the job offers for the company.
    """
    company_id = current_user.company.id if current_user.company else None

    if not company_id:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Company not found."}
        )

    # Query job offers with company picture
    job_offers = db.query(CompanyOffers).options(
        joinedload(CompanyOffers.company)  # Fetch related company details
    ).filter(
        CompanyOffers.company_id == company_id
    ).all()

    return templates.TemplateResponse(
        "job_ads_per_company.html",
        {"request": request, "job_offers": job_offers},
    )
