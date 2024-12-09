"""
This module contains the routes for the company ads
and the functions that handle the requests:
- create_new_ad_: Create a new ad for the company
- get_company_own_ads: Get all ads for the company
- update_company_ad: Update a company ad
- delete_company_ad_: Delete a company ad
"""
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.common import auth
from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.company import (
    CompanyAdModel,
    CompanyAdUpdateModel,
    CreateCompanyAdModel,
)
from app.data.schemas.skills import SkillCreate
from app.services.company_ad_service import (
    create_new_ad,
    delete_company_ad,
    get_company_ads,
    edit_company_ad_by_id,
)


job_ad_router = APIRouter(prefix="/ads", tags=["Company Ads"])


# WORKS
templates = Jinja2Templates(directory="app/templates")
# WORKS
@job_ad_router.api_route("/create", methods=["GET", "POST"], response_class=HTMLResponse)
async def create_company_ad(request: Request, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    if request.method == "GET":
        return templates.TemplateResponse("job_add_create.html", {"request": request})

    if request.method == "POST":
        form_data = await request.form()

        # Extract the form data
        title = form_data.get("title")
        min_salary = int(form_data.get("min_salary", 0))
        max_salary = int(form_data.get("max_salary", 0))
        description = form_data.get("description")
        location = form_data.get("location")
        status = form_data.get("status", "Active")

        skills_input = form_data.getlist("skills[]")
        levels_input = form_data.getlist("levels[]")
        skills = [
            SkillCreate(name=skill, level=level)
            for skill, level in zip(skills_input, levels_input)
        ]
        company_ad_data = CreateCompanyAdModel(
            title=title,
            min_salary=min_salary,
            max_salary=max_salary,
            description=description,
            location=location,
            status=status,
            skills=skills
        )

        create_new_ad(
            title=company_ad_data.title,
            min_salary=company_ad_data.min_salary,
            max_salary=company_ad_data.max_salary,
            job_description=company_ad_data.description,
            location=company_ad_data.location,
            status=company_ad_data.status,
            current_user=current_user,
            db=db
        )

        return RedirectResponse("/", status_code=303)


@job_ad_router.get("/info", response_model=List[CompanyAdModel])
def get_company_own_ads(
    current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)
):
    """
    Get all ads for the company
    Returns a list of ads
    """
    ads = get_company_ads(current_user=current_user, db=db)
    return ads or []


@job_ad_router.put("/{ad_id}", response_model=CompanyAdModel)
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


@job_ad_router.delete("/{id}")
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
