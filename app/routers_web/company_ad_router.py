import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.common import auth
from app.data.database import get_db
from app.data.models import User, CompanyOffers, Location
from app.data.schemas.company import CompanyAdModel, CompanyAdUpdateModel, CreateCompanyAdModel
from app.services.company_ad_service import create_new_ad, delete_company_ad, get_company_ads, edit_company_ad_by_id
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
        db=db
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






# WORKS ? Check it again
@company_ad_router_web.delete('/{id}')
def delete_company_ad_(
        ad_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    return delete_company_ad(ad_id=ad_id, db=db, current_user=current_user)


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