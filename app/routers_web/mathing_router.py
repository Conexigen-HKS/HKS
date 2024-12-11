from fastapi import Request, Depends, HTTPException, APIRouter, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import User, ProfessionalProfile, RequestsAndMatches, CompanyOffers, Companies
from app.data.schemas.matches import MatchRequest
from app.services.mailjet_service import send_email
from app.services.match_service import remove_job_offer, send_match_request

match_web_router = APIRouter(prefix="/matches", tags=["Matches"])
templates = Jinja2Templates(directory="app/templates")


@match_web_router.get("/", response_class=HTMLResponse)
async def job_matching(
    request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access forbidden for non-professionals")
    
    professional_profile = db.query(ProfessionalProfile).filter_by(user_id=current_user.id).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    
    excluded_offers = db.query(RequestsAndMatches.company_offers_id).filter_by(
        professional_profile_id=professional_profile.id
    ).all()
    excluded_offer_ids = [offer[0] for offer in excluded_offers]
    
    random_job = (
        db.query(CompanyOffers)
        .filter(~CompanyOffers.id.in_(excluded_offer_ids))
        .order_by(func.random())
        .first()
    )
    
    if not random_job:
        return templates.TemplateResponse(
            "no_jobs.html",
            {"request": request, "message": "No more job ads available!"},
        )
    
    active_applications = db.query(ProfessionalProfile).filter_by(user_id=current_user.id, status="active").all()
    jobs = [{
        "id": random_job.id,
        "description": random_job.description,
        "location": random_job.location.city_name if random_job.location else "N/A",
        "min_salary": random_job.min_salary,
        "max_salary": random_job.max_salary,
        "skills": [skill.name for skill in random_job.skills],
    }]
    
    return templates.TemplateResponse(
        "matching_job_ads.html",
        {
            "request": request,
            "jobs": jobs,
            "active_applications": active_applications,
        },
    )

@match_web_router.post("/match_request", response_class=HTMLResponse)
async def match_request(
    request: Request,
    match_data: MatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access forbidden for non-professionals")

    # Извличане на данните от модела
    target_id = match_data.target_id
    action = match_data.action
    profile_or_offer_id = match_data.profile_or_offer_id

    if action == "like":
        if not profile_or_offer_id:
            raise HTTPException(status_code=400, detail="Profile ID is required for liking a job.")
        # Използвайте функцията от match_service.py
        try:
            response = send_match_request(
                db=db,
                target_id=target_id,
                current_user=current_user,
                profile_or_offer_id=profile_or_offer_id
            )
        except HTTPException as e:
            return templates.TemplateResponse("confirmation.html", {"request": request, "message": e.detail})
        return templates.TemplateResponse("confirmation.html", {"request": request, "message": response["message"]})
    
    elif action == "dislike":
        # Промахване на обявата без изпращане на match request
        try:
            remove_job_offer(db=db, target_id=target_id, current_user=current_user)
        except HTTPException as e:
            return templates.TemplateResponse("confirmation.html", {"request": request, "message": e.detail})
        return templates.TemplateResponse("confirmation.html", {"request": request, "message": "Job ad dismissed successfully"})
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


@match_web_router.get("/apps/", response_class=HTMLResponse)
async def application_matching(
    request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Access forbidden for non-companies")

    # Fetch company profile
    company = db.query(Companies).filter_by(user_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")

    # Fetch all applications not liked/disliked by the company
    excluded_apps = db.query(RequestsAndMatches.professional_profile_id).filter_by(
        company_offers_id=company.id
    ).all()
    excluded_app_ids = [app[0] for app in excluded_apps]

    # Get a random job application that hasn't been interacted with
    random_app = (
        db.query(ProfessionalProfile)
        .filter(~ProfessionalProfile.id.in_(excluded_app_ids))
        .order_by(func.random())
        .first()
    )

    # Handle case where no applications are available
    if not random_app:
        return templates.TemplateResponse(
            "no_applications.html",
            {"request": request, "message": "No more job applications available!"},
        )

    # Prepare application data for the template
    application_data = {
        "id": random_app.id,
        "title": random_app.description or "Untitled",
        "description": random_app.description,
        "location": random_app.location.city_name if random_app.location else "N/A",
        "min_salary": random_app.min_salary,
        "max_salary": random_app.max_salary,
        "status": random_app.status,
        "picture": random_app.professional.picture,
        "professional_name": f"{random_app.professional.first_name} {random_app.professional.last_name}",
        "email": random_app.professional.email,
    }

    # Return the application details to the template
    return templates.TemplateResponse(
        "matching_job_app.html",
        {"request": request, "application": application_data},
    )


@match_web_router.post("/apps/match_application", response_class=HTMLResponse)
async def match_application(
    request: Request,
    target_id: str = Form(...),
    action: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Access forbidden for non-companies")

    # Fetch company profile
    company = db.query(Companies).filter_by(user_id=current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")

    # Get professional profile being liked/disliked
    professional_profile = db.query(ProfessionalProfile).filter_by(id=target_id).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    # Check for an existing entry where the current company liked/disliked this professional
    existing_entry = db.query(RequestsAndMatches).filter_by(
        company_offers_id=company.id,
        professional_profile_id=professional_profile.id,
    ).first()

    # Check if the professional has already liked the company's offer
    reverse_entry = db.query(RequestsAndMatches).filter_by(
        company_offers_id=professional_profile.chosen_company_offer_id,  # Assuming this tracks mutual interest
        professional_profile_id=company.id,
    ).first()

    if not existing_entry:
        # Create a new entry if no existing interaction
        new_request = RequestsAndMatches(
            professional_profile_id=professional_profile.id,
            company_offers_id=company.id,
            match=reverse_entry is not None and reverse_entry.match is True,
        )
        db.add(new_request)

    elif action == "like":
        # Update existing entry to "like" and handle mutual match
        existing_entry.match = reverse_entry is not None and reverse_entry.match is True

    db.commit()

    # Notify users if there's a mutual match
    if existing_entry.match or (reverse_entry and reverse_entry.match):
        # Send notifications for mutual match
        subject = "Mutual Match Found!"
        text_content = (
            f"Congratulations, {professional_profile.professional.first_name}! "
            f"You and {company.name} have a mutual match."
        )
        html_content = f"<p>{text_content}</p>"
        send_email(
            to_email=professional_profile.professional.email,
            to_name=f"{professional_profile.professional.first_name} {professional_profile.professional.last_name}",
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )

    message = f"You have {'liked' if action == 'like' else 'disliked'} the application."
    return templates.TemplateResponse("confirmation.html", {"request": request, "message": message})