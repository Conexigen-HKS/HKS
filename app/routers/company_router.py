from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from app.common import auth
from app.common.auth import get_current_user
from app.data.database import Session, get_db
from app.data.models import User, ProfessionalProfile, Location
from app.data.schemas.company import CompanyInfoModel, CompanyAdModel, CompanyAdModel2, ShowCompanyModel, \
    CompanyInfoRequestModel
from app.data.schemas.job_application import JobApplicationResponse
from app.services.company_service import (edit_company_description_service,
                                          get_company_name_by_username_service,
                                          find_all_companies_service,

                                          get_company_id_by_user_id_service,
                                          show_company_description_service)
from app.services.jop_ap_service import get_active_job_applications_service, search_job_applications_service


from app.common import auth
from app.common.auth import decode_access_token
from app.data.database import Session, get_db
from app.data.models import User
from app.data.schemas.company import CompanyInfoModel, CompanyAdModel, CompanyAdModel2, ShowCompanyModel
from app.services.company_service import (edit_company_description_service,
                                          get_company_name_by_username_service,
                                          find_all_companies_service,

                                          get_company_id_by_user_id_service,
                                          show_company_description_service)
company_router = APIRouter(prefix="/companies", tags=["Companies"])


@company_router.get("/info", response_model=List[ShowCompanyModel])
def show_company_description(
        current_user: User = Depends(auth.get_current_user),
        db: Session = Depends(get_db)
):
    show_company = show_company_description_service(user=current_user, db=db)

    if show_company:
        return [show_company]
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while #fixthis company description"
        )

@company_router.put('/info')
def edit_company_description(
    company_info: CompanyInfoRequestModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    company_username = current_user.username

    if not company_username:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"

        )
    updated_company = edit_company_description_service(company_info, company_username, db=db)

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


@company_router.get("/active-job-applications", response_model=List[JobApplicationResponse])
def get_active_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    company_id = get_company_id_by_user_id_service(current_user.id)
    if not company_id:
        raise HTTPException(status_code=403, detail="Only companies can access this endpoint")

    return get_active_job_applications_service(db)


@company_router.get("/active-job-applications", response_model=List[JobApplicationResponse])
def get_active_job_applications(
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    company_id = get_company_id_by_user_id_service(current_user.id)
    if not company_id:
        raise HTTPException(status_code=403, detail="Only companies can access this endpoint")

    return get_active_job_applications_service(db)


@company_router.get("/search-job-applications", response_model=List[JobApplicationResponse])
def search_job_applications(
        query: Optional[str] = Query(None),
        location: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    company_id = get_company_id_by_user_id_service(current_user.id)
    if not company_id:
        raise HTTPException(status_code=403, detail="Only companies can access this endpoint")

    return search_job_applications_service(db, query, location)
