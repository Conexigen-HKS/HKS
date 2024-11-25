from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.common.auth import decode_access_token
from app.data.schemas.company import CompanyInfoModel, CompanyAdModel, CompanyAdModel2, ShowCompanyModel
from app.services.company_service import (edit_company_description_service,
                                          get_company_name_by_username_service,
                                          find_all_companies_service,
                                          create_new_ad_service,
                                          get_company_id_by_user_id_service, edit_company_ad_by_position_title_service,
                                          get_company_ads_service, show_company_description_service)
company_router = APIRouter(prefix="/companies", tags=["Companies"])

@company_router.get("/companies/companies/info", response_model=List[ShowCompanyModel])
def show_company_description(token: str = Query(...)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
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
    show_company = show_company_description_service(username)

    if show_company:
        return [show_company]
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while updating the company description"
        )

@company_router.put('/companies/info')
def edit_company_description(company_info: CompanyInfoModel, token: str = Query(..., alias="token")):
    try:
        payload = decode_access_token(token)
        company_username = payload.get("sub")

        if company_username is None:
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

    updated_company = edit_company_description_service(company_info, company_username)

    if updated_company:
        return {"message": "Company description updated successfully", "company": updated_company}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while updating the company description"
        )


@company_router.post('/company/create/ad')
def create_new_ad(company_ad: CompanyAdModel, token: str = Query(..., alias="token")):
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

    new_ad = create_new_ad_service(company_id, company_ad.position_title, company_ad.min_salary, company_ad.max_salary,
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


@company_router.get('/company/ads', response_model=List[Optional[CompanyAdModel]])
def get_company_ads(token: Optional[str] = Query(None)):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )

    payload = decode_access_token(token)
    user_username = payload.get("id")
    ads = get_company_ads_service(user_username)

    return ads or {}


@company_router.put('/company/ad/{ad_id}', response_model=CompanyAdModel2)
def update_company_ad(add_title: str, ad_info: CompanyAdModel2, token: str = Query(...)):
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )
    payload = decode_access_token(token)
    company_username = payload.get("id")
    return edit_company_ad_by_position_title_service(add_title, ad_info, company_username)


@company_router.get('/all')
async def show_all_companies():
    companies = find_all_companies_service()
    return companies
