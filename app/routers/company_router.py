from typing import List, Optional

from fastapi import APIRouter, Response, HTTPException, Query
from starlette import status
from app.common.auth import decode_access_token
from app.data.schemas.company import CompanyInfoModel, CompanyAdModel,CompanyAdModel2
from app.services.company_service import (edit_company_description_service,
                                          get_company_name_by_username_service,
                                           edit_company_description_service,
                                          find_all_companies_service,)
company_router = APIRouter(prefix="/companies", tags=["Companies"])




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


# @company_router.post('/company/create/ad')
# def create_new_ad(company_ad: CompanyAdModel, token: str = Query(..., alias="token")):
#     try:
#         payload = decode_access_token(token)
#         company_username = payload.get("username")
#
#         if company_username is None:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Could not validate credentials"
#             )
#         company_id = payload.get("id")
#         company_name = get_company_name_by_username_service(company_username)
#     except Exception as e:
#         raise HTTPException(
#             status_code=401,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"}
#         )
#     new_ad = create_new_ad_service(company_id, company_ad.position_title, company_ad.salary,
#                                    company_ad.job_description, company_ad.location, company_ad.ad_status)
#     if new_ad:
#         return {"message": "Ad added successfully",
#                 "Company name": company_name,
#                 "Title": company_ad.position_title,
#                 "salary": company_ad.salary,
#                 "description": company_ad.job_description,
#                 "location": company_ad.location,
#                 "status": company_ad.ad_status
#                 }
#
#
# @company_router.get('/company/ads', response_model=List[Optional[CompanyAdModel]])
# def get_company_ads(token: Optional[str] = Query(None)):
#     if token is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Token is missing"
#         )
#
#     payload = decode_access_token(token)
#     company_username = payload.get("username")
#     ads = get_company_ads_service(company_username)
#
#     return ads or []
#
#
# @company_router.put('/company/ad/{ad_id}', response_model=CompanyAdModel2)
# def update_company_ad(ad_id: int, ad_info: CompanyAdModel2, token: str = Query(...)):
#     if token is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Token is missing"
#         )
#     payload = decode_access_token(token)
#     company_username = payload.get("username")
#     return edit_company_ad_by_id_service(ad_id, ad_info, company_username)


@company_router.get('/all')
async def show_all_companies():
    companies = find_all_companies_service()
    return companies
