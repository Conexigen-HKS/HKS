import uuid
from http.client import HTTPException
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.common import auth
from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User, CompanyOffers, Location, Companies
from app.data.schemas.company import CompanyAdModel, CreateCompanyAdModel
from app.services.company_ad_service import create_new_ad
from app.services.job_app_service import search_job_ads_service

company_ad_router_web = APIRouter(prefix="/ads", tags=["Company Ads"])

templates = Jinja2Templates(directory="app/templates")


# WORKS
@company_ad_router_web.post('/new_ad')
def create_new_ad_(
        company_ad: CreateCompanyAdModel,
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    new_ad = create_new_ad(
        title=company_ad.title,
        min_salary=company_ad.min_salary,
        max_salary=company_ad.max_salary,
        job_description=company_ad.description,
        location=company_ad.location,
        status=company_ad.status,
        current_user=current_user,
        db=db,
        skills=company_ad.skills
    )
    return {
        "message": "Ad added successfully",
        "ad": CompanyAdModel(
            company_name=new_ad.company.name,
            company_ad_id=new_ad.id,
            title=new_ad.title,
            min_salary=new_ad.min_salary,
            max_salary=new_ad.max_salary,
            description=new_ad.description,
            location=new_ad.location.city_name if new_ad.location else "N/A",
            status=new_ad.status,
        )
    }




@company_ad_router_web.get('/search', response_class=HTMLResponse)
def search_ads(
        request: Request,
        db: Session = Depends(get_db),
        keyword: Optional[str] = "",
        location: Optional[str] = "",
        min_salary: Optional[int] = 0,
        max_salary: Optional[int] = 0,
        page: int = 1,
        per_page: int = 10
):
    job_ads = search_job_ads_service(
        db=db,
        query=keyword,
        location=location,
        min_salary=min_salary,
        max_salary=max_salary,
        order_by="asc"
    )

    total_count = len(job_ads)
    total_pages = (total_count + per_page - 1) // per_page
    job_ads_paginated = job_ads[(page - 1) * per_page: page * per_page]

    return templates.TemplateResponse(
        "job_listings.html",
        {
            "request": request,
            "ads": job_ads_paginated,
            "current_page": page,
            "total_pages": total_pages,
            "keyword": keyword,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary,
        },
    )



@company_ad_router_web.get("/{offer_id}", response_class=HTMLResponse)
def view_company_offer_details(
    offer_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    View the details of a single company offer.
    """
    offer = (
        db.query(CompanyOffers)
        .join(Companies, Companies.id == CompanyOffers.company_id)
        .join(Location, Location.id == CompanyOffers.location_id, isouter=True)
        .filter(CompanyOffers.id == offer_id)
        .first()
    )

    if not offer:
        raise HTTPException(status_code=404, detail="Company offer not found.")

    # Check ownership
    is_owner = offer.company.user_id == current_user.id

    # Fetch related skills
    skills = [
        f"{req.skill.name} ({req.level})"
        for req in offer.requirements
    ]

    offer_data = {
        "id": offer.id,
        "title": offer.title,
        "description": offer.description,
        "company_name": offer.company.name,
        "company_logo": offer.company.picture,
        "location": offer.location.city_name if offer.location else "Unknown",  # Get city name
        "min_salary": offer.min_salary,
        "max_salary": offer.max_salary,
        "status": offer.status,
        "skills": skills,
    }

    return templates.TemplateResponse(
        "job_ad_single.html",
        {"request": request, "offer": offer_data, "is_owner": is_owner},
    )


@company_ad_router_web.put("/archive/{offer_id}")
def archive_company_offer(
    offer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Archive a company offer by setting its status to "Archived".
    """
    offer = db.query(CompanyOffers).filter(CompanyOffers.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Company offer not found.")

    if offer.company.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to archive this offer."
        )

    offer.status = "Archived"
    db.commit()

    return {"message": "Company offer archived successfully."}
