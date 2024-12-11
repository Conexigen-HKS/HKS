# app/routers_web/job_search_router.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from typing import Optional

from app.data.database import get_db
from app.services.job_app_service import search_job_ads_service

job_search_router = APIRouter(prefix="/job_search", tags=["Job Search"])
templates = Jinja2Templates(directory="app/templates")

@job_search_router.get("/", response_class=HTMLResponse)
async def search_jobs(
    request: Request,
    db: Session = Depends(get_db),
    keyword: Optional[str] = "",
    location: Optional[str] = "",
    min_salary: Optional[int] = 0,
    max_salary: Optional[int] = 0,
    page: int = 1,
    per_page: int = 10
):
    job_ads = search_job_ads_service(
        db=db,
        query=keyword,
        location=location,
        min_salary=min_salary,
        max_salary=max_salary,
        order_by="asc"
    )

    total_count = len(job_ads)
    total_pages = (total_count + per_page - 1) // per_page
    job_ads_paginated = job_ads[(page - 1) * per_page: page * per_page]

    return templates.TemplateResponse(
        "job_listings.html",
        {
            "request": request,
            "ads": job_ads_paginated,
            "current_page": page,
            "total_pages": total_pages,
            "keyword": keyword,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary,
        },
    )