from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Header

from app.common.auth import decode_access_token
from app.data.schemas.company import CompanyInfoModel, CompanyAdModel, CompanyAdModel2, ShowCompanyModel
from app.services.company_service import (edit_company_description_service,
                                          get_company_name_by_username_service,
                                          find_all_companies_service,

                                          get_company_id_by_user_id_service,
                                          show_company_description_service)
company_router = APIRouter(prefix="/companies", tags=["Companies"])

@company_router.get("/info", response_model=List[ShowCompanyModel])
def show_company_description(token: str = Header(..., alias="token")):
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

@company_router.put('/info')
def edit_company_description(company_info: CompanyInfoModel, token: str = Header(..., alias="token")):
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





@company_router.get('/all')
async def show_all_companies():
    companies = find_all_companies_service()
    return companies
