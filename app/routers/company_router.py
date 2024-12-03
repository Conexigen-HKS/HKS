from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Query, Depends
from app.common import auth
from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.company import ShowCompanyModel, CompanyInfoRequestModel
from app.data.schemas.job_application import JobApplicationResponse
from app.services.company_service import (edit_company_description_service,
find_all_companies_service,show_company_description_service)
from app.services.job_app_service import search_job_applications_service


company_router = APIRouter(prefix="/companies", tags=["Companies"])


#WORKS
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
        )

#WORKS
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

#WORKS
@company_router.get('/all')
def show_all_companies(db: Session = Depends(get_db)):
    companies = find_all_companies_service(db=db)
    return companies

#WORKS
@company_router.get("/job-applications", response_model=List[JobApplicationResponse])
def search_or_get_job_applications(
        query: Optional[str] = Query(None),
        location: Optional[str] = Query(None),
        skill: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    if current_user.role != 'company':
        raise HTTPException(status_code=403, detail="Only companies can access this endpoint")
    
    return search_job_applications_service(db, query, location, skill)