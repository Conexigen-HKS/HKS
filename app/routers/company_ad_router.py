"""
This module contains the routes for the company ads
and the functions that handle the requests:
- create_new_ad_: Create a new ad for the company
- get_company_own_ads: Get all ads for the company
- update_company_ad: Update a company ad
- delete_company_ad_: Delete a company ad
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common import auth
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.company import (
    CompanyAdModel,
    CompanyAdUpdateModel,
    CreateCompanyAdModel,
)
from app.services.company_ad_service import (
    create_new_ad,
    delete_company_ad,
    get_company_ads,
    edit_company_ad_by_id,
)


company_ad_router = APIRouter(prefix="/api/ads", tags=["Company Ads"])


# WORKS
@company_ad_router.post("/new_ad")
def create_new_ad_(
    company_ad: CreateCompanyAdModel,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new ad for the company
    Accepts the following parameters:
    - title: str
    - min_salary: float
    - max_salary: float
    - description: str
    - location: str
    - status: str
    Returns a message and the created ad
    """
    new_ad = create_new_ad(
        title=company_ad.title,
        min_salary=company_ad.min_salary,
        max_salary=company_ad.max_salary,
        job_description=company_ad.description,
        location=company_ad.location,
        status=company_ad.status,
        current_user=current_user,
        db=db,
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
        ),
    }


@company_ad_router.get("/info", response_model=List[CompanyAdModel])
def get_company_own_ads(
    current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    """
    Get all ads for the company
    Returns a list of ads
    """
    ads = get_company_ads(current_user=current_user, db=db)
    return ads or []


@company_ad_router.put("/{ad_id}", response_model=CompanyAdModel)
def update_company_ad(
    ad_id: str,
    ad_info: CompanyAdUpdateModel,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a company ad
    Accepts the following parameters:
    - title: str
    - min_salary: float
    - max_salary: float
    - description: str
    - location: str
    - status: str
    Returns the updated ad
    """
    return edit_company_ad_by_id(
        job_ad_id=ad_id, ad_info=ad_info, current_company=current_user, db=db
    )


@company_ad_router.delete("/{id}")
def delete_company_ad_(
    ad_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Delete a company ad
    Accepts the following parameters:
    - ad_id: str
    Returns a message and the deleted ad
    """
    return delete_company_ad(ad_id=ad_id, db=db, current_user=current_user)
