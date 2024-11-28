from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.services.company_service import get_company_id_by_user_id_service
from app.services.job_ad_service import (
    create_new_ad_service,
    edit_company_ad_by_position_title_service,
    get_company_ads_service,
)
from app.data.schemas.job_ad import CompanyAdModel, CompanyAdModel2
from app.data.database import get_db
from app.common.auth import get_current_user, UserAuthDep
from app.data.models import User, CompanyOffers

company_ad_router = APIRouter(prefix="/ads", tags=["Company Ads"])
@company_ad_router.post('/new_ad')
def create_new_ad(
    company_ad: CompanyAdModel,
    current_user: UserAuthDep,
    db: Session = Depends(get_db)
):
    try:
        user_id = current_user.id
        company_id = get_company_id_by_user_id_service(user_id, db)
        company_name = current_user.company_name

        new_ad = CompanyOffers(
            company_id=str(company_id),
            position_title=company_ad.position_title,
            min_salary=company_ad.min_salary,
            max_salary=company_ad.max_salary,
            description=company_ad.description,
            location=company_ad.location,
            status=company_ad.status
        )

        db.add(new_ad)
        db.commit()

        return {
            "message": "Ad added successfully",
            "Company name": company_name,
            "Title": company_ad.position_title,
            "Minimum Salary": company_ad.min_salary,
            "Maximum Salary": company_ad.max_salary,
            "Description": company_ad.description,
            "Location": company_ad.location,
            "Status": company_ad.status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@company_ad_router.get('/info', response_model=List[Optional[CompanyAdModel]])
def get_company_ads(
    current_user: UserAuthDep,
    db: Session = Depends(get_db)
):
    try:
        company_id = get_company_id_by_user_id_service(current_user.id, db)
        ads = db.query(CompanyOffers).filter(CompanyOffers.company_id == company_id).all()
        return [
            CompanyAdModel(
                company_ad_id=str(ad.id),
                position_title=ad.position_title,
                min_salary=ad.min_salary,
                max_salary=ad.max_salary,
                description=ad.description,
                location=ad.location,
                status=ad.status
            ) for ad in ads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@company_ad_router.put('/ad/{ad_id}', response_model=CompanyAdModel2)
def update_company_ad(
    ad_id: str,
    ad_info: CompanyAdModel2,
    current_user: UserAuthDep,
    db: Session = Depends(get_db)
):
    try:
        company_id = get_company_id_by_user_id_service(current_user.id, db)

        # Find the ad
        ad = db.query(CompanyOffers).filter(
            CompanyOffers.id == ad_id,
            CompanyOffers.company_id == company_id
        ).first()

        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        # Update fields
        if ad_info.position_title:
            ad.position_title = ad_info.position_title
        if ad_info.min_salary:
            ad.min_salary = ad_info.min_salary
        if ad_info.max_salary:
            ad.max_salary = ad_info.max_salary
        if ad_info.description:
            ad.description = ad_info.description
        if ad_info.location:
            ad.location = ad_info.location
        if ad_info.status is not None:
            ad.status = ad_info.status

        db.commit()

        return CompanyAdModel2(
            position_title=ad.position_title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location,
            status=ad.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
