from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header
from app.common.auth import decode_access_token
from app.data.schemas.company import CompanyAdModel, CompanyAdModel2
from app.services.company_ad_service import create_new_ad_service, get_company_ads_service, \
    edit_company_ad_by_position_title_service, get_company_all_ads_service
from app.services.company_service import get_company_name_by_username_service, get_company_id_by_user_id_service


company_ad_router = APIRouter(prefix="/ads", tags=["Company Ads"])


@company_ad_router.post('/new_ad')
def create_new_ad(company_ad: CompanyAdModel, token: str = Header(..., alias="token")):
    try:
        payload = decode_access_token(token)
        user_username = payload.get("sub")
        user_id = payload.get("id")
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

    new_ad = create_new_ad_service(str(company_id), company_ad.position_title, company_ad.min_salary,
                                   company_ad.max_salary,
                                   company_ad.description, company_ad.location, company_ad.status)
    if new_ad:
        return {"message": "Ad added successfully",
                "Company name": company_name,
                "Title": company_ad.position_title,
                "Minimum Salary": company_ad.min_salary,
                "Maximum Salary": company_ad.max_salary,
                "description": company_ad.description,
                "location": company_ad.location,
                "status": company_ad.status
                }


@company_ad_router.get('/info', response_model=List[Optional[CompanyAdModel]])
def get_company_own_ads(token: str = Header(..., alias="token")):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )

    payload = decode_access_token(token)
    user_id = payload.get("id")
    company_id = get_company_id_by_user_id_service(user_id)
    company_name = get_company_name_by_username_service(company_id)
    ads = get_company_ads_service(user_id, company_name)

    return ads or []


@company_ad_router.put('/ad/{ad_id}', response_model=CompanyAdModel2)
def update_company_ad(add_title: str, ad_info: CompanyAdModel2, token: str = Header(..., alias="token")):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )
    payload = decode_access_token(token)
    company_username = payload.get("id")
    return edit_company_ad_by_position_title_service(add_title, ad_info, company_username)


@company_ad_router.get('/all_ads', response_model=List[Optional[CompanyAdModel]])
def get_all_company_ads():

    ads = get_company_all_ads_service()

    return ads or []
