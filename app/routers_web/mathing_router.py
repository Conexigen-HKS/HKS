from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User, ProfessionalProfile, RequestsAndMatches, CompanyOffers, Companies
from app.services.mailjet_service import send_email

match_web_router = APIRouter(prefix="/matches", tags=["Matches"])
templates = Jinja2Templates(directory="app/templates")

class MatchRequest(BaseModel):
    target_id: str
    action: str  # "like" or "dislike"

@match_web_router.get("/", response_class=HTMLResponse)
async def job_matching(
    request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access forbidden for non-professionals")

    # Get the professional profile
    professional_profile = db.query(ProfessionalProfile).filter_by(user_id=current_user.id).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    # Fetch all job offers not liked/disliked by the user
    excluded_offers = db.query(RequestsAndMatches.company_offers_id).filter_by(
        professional_profile_id=professional_profile.id
    ).all()
    excluded_offer_ids = [offer[0] for offer in excluded_offers]

    # Get a random job that hasn't been interacted with
    random_job = (
        db.query(CompanyOffers)
        .filter(~CompanyOffers.id.in_(excluded_offer_ids))
        .order_by(func.random())
        .first()
    )

    # Handle case where no jobs are available
    if not random_job:
        return templates.TemplateResponse(
            "no_jobs.html",
            {"request": request, "message": "No more job ads available!"},
        )

    # Return the job details to the template
    return templates.TemplateResponse(
        "matching_job_ads.html",
        {
            "request": request,
            "job": {
                "id": random_job.id,
                "title": random_job.title,
                "company_name": random_job.company.name,
                "location": random_job.location.city_name if random_job.location else "N/A",
                "min_salary": random_job.min_salary,
                "max_salary": random_job.max_salary,
                "description": random_job.description,
                "requirements": random_job.requirements,
            },
        },
    )

@match_web_router.post("/match_request", response_class=HTMLResponse)
async def match_request(
    request: Request,
    target_id: str = Form(...),
    action: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Handle match requests (like/dislike) for a job offer.
    """
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access forbidden for non-professionals")

    # Get professional profile
    professional_profile = db.query(ProfessionalProfile).filter_by(user_id=current_user.id).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    # Get company offer
    company_offer = db.query(CompanyOffers).filter_by(id=target_id).first()
    if not company_offer:
        raise HTTPException(status_code=404, detail="Company offer not found")

    # Check if there's already a match/dislike entry
    existing_entry = db.query(RequestsAndMatches).filter_by(
        professional_profile_id=professional_profile.id,
        company_offers_id=company_offer.id
    ).first()

    if not existing_entry:
        # Create a new match request
        new_request = RequestsAndMatches(
            professional_profile_id=professional_profile.id,
            company_offers_id=company_offer.id,
            match=(action == "like"),
        )
        db.add(new_request)

        # Notify the company via email on new match request
        if action == "like":
            company = db.query(Companies).filter(Companies.id == company_offer.company_id).first()
            if company and company.email:
                subject = "New match request"
                text_content = f"Hello {company.name},\n\nYou have a new match request from {current_user.username}."
                html_content = f"<p>Hello {company.name},</p><p>You have a new match request from {current_user.username}.</p>"
                send_email(
                    to_email=company.email,
                    to_name=company.name,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content
                )
    elif action == "like":
        existing_entry.match = True

        # Notify the company via email on match confirmation
        company = db.query(Companies).filter(Companies.id == company_offer.company_id).first()
        if company and company.email:
            subject = "New confirmed match"
            text_content = f"Hello {company.name},\n\nYou have a new confirmed match with {current_user.username}."
            html_content = f"<p>Hello {company.name},</p><p>You have a new confirmed match with {current_user.username}.</p>"
            send_email(
                to_email=company.email,
                to_name=company.name,
                subject=subject,
                text_content=text_content,
                html_content=html_content
            )

    db.commit()

    # Return confirmation response
    message = f"You have {'liked' if action == 'like' else 'disliked'} the job."
    return templates.TemplateResponse("confirmation.html", {"request": request, "message": message})
