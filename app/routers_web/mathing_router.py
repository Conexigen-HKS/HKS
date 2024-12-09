import random

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.common import auth
from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import CompanyOffers, User
from app.services.match_service import send_match_request, view_matches

match_router_web = APIRouter(prefix='/matches', tags=['Matches'])

templates = Jinja2Templates(directory="app/templates")



@match_router_web.get("/", response_class=HTMLResponse)
async def matches_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Display all matches for the current user
    """
    matches = view_matches(db=db, current_user=current_user)
    return templates.TemplateResponse(
        "matches_dashboard.html",
        {
            "request": request,
            "matches": matches["matches"],
            "user_role": current_user.role,
        },
    )


@match_router_web.get("/random", response_class=HTMLResponse)
async def get_random_job(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Render a random job ad as an HTML page
    """
    job_ads = db.query(CompanyOffers).filter(CompanyOffers.status == "Active").all()

    if not job_ads:
        return templates.TemplateResponse(
            "no_jobs.html", {"request": request, "message": "No active job ads available."}
        )

    random_job = random.choice(job_ads)
    requirements = [
        {
            "title": req.skill.name,
            "level": req.level,
        }
        for req in random_job.requirements
    ] if random_job.requirements else []

    return templates.TemplateResponse(
        "matching_job_ads.html",
        {
            "request": request,
            "company_name": random_job.company.name,
            "title": random_job.title,
            "min_salary": random_job.min_salary,
            "max_salary": random_job.max_salary,
            "description": random_job.description,
            "location": random_job.location,
            "requirements": requirements,
            "target_id": random_job.id,
        },
    )


@match_router_web.post("/match_request", response_class=HTMLResponse)
async def send_match_request_web(
    target_id: str = Form(...),
    action: bool = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process a match request (like or dislike) and redirect to matches dashboard
    """
    send_match_request(db=db, target_id=target_id, current_user=current_user)
    return templates.TemplateResponse(
        "confirmation.html", {"request": request, "message": "Action processed successfully"}
    )