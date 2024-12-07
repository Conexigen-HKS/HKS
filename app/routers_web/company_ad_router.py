import uuid
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.common import auth
from app.data.database import get_db
from app.data.models import User, CompanyOffers, Location
from app.data.schemas.company import CompanyAdModel, CompanyAdUpdateModel, CreateCompanyAdModel
from app.services.company_ad_service import create_new_ad, delete_company_ad, get_company_ads, edit_company_ad_by_id

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


@company_ad_router_web.get('/info', response_model=List[CompanyAdModel])
def get_company_own_ads(current_user: User = Depends(auth.get_current_user),
                        db: Session = Depends(get_db)):
    ads = get_company_ads(current_user=current_user, db=db)
    return ads or []


@company_ad_router_web.put('/{ad_id}', response_model=CompanyAdModel)
def update_company_ad(
        ad_id: str,
        ad_info: CompanyAdUpdateModel,
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    return edit_company_ad_by_id(
        job_ad_id=ad_id,
        ad_info=ad_info,
        current_company=current_user,
        db=db
    )


# @company_ad_router.get('/all_ads', response_model=List[Optional[CompanyAdModel]])
# def get_all_company_ads():

#     ads = get_company_all_ads_service()

#     return ads or []

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
        page: int = 1,
        per_page: int = 10,
        keyword: str = "",
        location: str = "",
        category: str = "",
        min_salary: int = 0,
        max_salary: int = 0,
        db: Session = Depends(get_db)
):
    query = db.query(CompanyOffers).join(Location).filter(CompanyOffers.status == "Active")

    if keyword:
        query = query.filter(CompanyOffers.title.ilike(f"%{keyword}%"))
    if location:
        query = query.filter(Location.city_name.ilike(f"%{location}%"))
    if min_salary > 0 and max_salary > 0:
        query = query.filter(
            (CompanyOffers.min_salary <= max_salary) &
            (CompanyOffers.max_salary >= min_salary)
        )
    elif min_salary > 0:
        query = query.filter(CompanyOffers.max_salary >= min_salary)
    elif max_salary > 0:
        query = query.filter(CompanyOffers.min_salary <= max_salary)

    total_count = query.count()
    total_pages = (total_count + per_page - 1) // per_page

    ads = query.offset((page - 1) * per_page).limit(per_page).all()

    ads_data = [
        CompanyAdModel(
            company_name=ad.company.name,
            company_ad_id=ad.id,
            title=ad.title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location.city_name if ad.location else "N/A",
            status=ad.status,
        )
        for ad in ads
    ]

    return templates.TemplateResponse(
        "job_listings.html",
        {
            "request": request,
            "ads": ads_data,
            "current_page": page,
            "total_pages": total_pages,
            "keyword": keyword,
            "location": location,
            "category": category,
            "min_salary": min_salary,
            "max_salary": max_salary,
        },
    )

