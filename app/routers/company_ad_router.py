import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header, Depends
from sqlalchemy.orm import Session
from app.common import auth
from app.common.auth import decode_access_token
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.company import CompanyAdModel, CompanyAdModel2, CompanyAdUpdateModel, CreateCompanyAdModel
from app.services.company_ad_service import create_new_ad_service, get_company_ads_service, edit_company_ad_by_id
# , get_company_all_ads_service, delete_company_ad_service
from app.services.company_service import get_company_name_by_username_service, get_company_id_by_user_id_service


company_ad_router = APIRouter(prefix="/ads", tags=["Company Ads"])


@company_ad_router.post('/new_ad')
def create_new_ad(company_ad: CreateCompanyAdModel, current_user: User = Depends(auth.get_current_user),
                  db: Session = Depends(get_db)):
    try:

        user_username = current_user.username
        user_id = current_user.id
        company_id = get_company_id_by_user_id_service(user_id)
        company_name = get_company_name_by_username_service(company_id)
        if user_username is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    new_ad = create_new_ad_service(company_id, company_ad.title, company_ad.min_salary, company_ad.max_salary,
                                   company_ad.description, company_ad.location, company_ad.status, db)
    if new_ad:
        return {"message": "Ad added successfully",
                "Company name": company_name,
                "Title": company_ad.title,
                "Minimum Salary": company_ad.min_salary,
                "Maximum Salary": company_ad.max_salary,
                "description": company_ad.description,
                "location": company_ad.location,
                "status": company_ad.status
                }


@company_ad_router.get('/info', response_model=List[CompanyAdModel])
def get_company_own_ads(current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)):

    ads = get_company_ads_service(current_user=current_user, db=db)
    return ads or []


@company_ad_router.put('/{ad_id}', response_model=CompanyAdModel)
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


# @company_ad_router.delete('/ad/{ad_id}')
# def delete_company_ad(ad_id: str, token: str = Header(..., alias="token")):
#     ad_id_uuid = uuid.UUID(ad_id)
#     if token is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Token is missing"
#         )
#     payload = decode_access_token(token)
#     user_id = payload.get("id")
#     company_id = get_company_id_by_user_id_service(user_id)
#     company_name = get_company_name_by_username_service(company_id)
#     return delete_company_ad_service(ad_id_uuid, user_id, company_name)
