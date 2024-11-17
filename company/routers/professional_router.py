from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query

from company.cummon.auth import decode_access_token
from company.models.company_model import CompanyAdModel
from company.services.professionals_service import show_all_ads_service

professional_router = APIRouter(prefix="/professionals", tags=["Professionals"])


@professional_router.get('/company/ads', response_model=List[Optional[CompanyAdModel]])
def get_company_ads(token: Optional[str] = Query(None)):

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )

    payload = decode_access_token(token)
    company_username = payload.get("username")
    ads = show_all_ads_service(company_username)

    return ads or []