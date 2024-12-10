from http.client import HTTPException

from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.common import auth
from app.data.database import get_db
from app.data.models import User, CompaniesRequirements, CompanyOffers
from app.services.match_service import send_match_request, view_matches

app = FastAPI()

templates = Jinja2Templates(directory="templates")

match_web_router = APIRouter(prefix="/matches", tags=["Matches"])

@match_web_router.get("/", response_class=HTMLResponse)
async def get_matches_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Render the match page.
    """
    return templates.TemplateResponse("matches.html", {"request": request, "user": current_user})


@match_web_router.get("/random", response_class=HTMLResponse)
async def get_random_job_ad(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Fetch a random job ad.
    """
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Only professionals can view job ads")

    job_offer = db.query(CompanyOffers).order_by(func.random()).first()

    if not job_offer:
        return {"message": "No job offers available"}

    requirements = db.query(CompaniesRequirements).filter(
        CompaniesRequirements.company_offers_id == job_offer.id
    ).all()

    requirements_list = [{"title": req.title, "level": req.level} for req in requirements]

    return {
        "id": str(job_offer.id),
        "title": job_offer.title,
        "company_name": job_offer.company.name,
        "location": job_offer.location.city_name if job_offer.location else "N/A",
        "min_salary": job_offer.min_salary,
        "max_salary": job_offer.max_salary,
        "description": job_offer.description,
        "requirements": requirements_list,
    }


@match_web_router.post("/match_request", response_class=HTMLResponse)
async def send_match(
    request: Request,
    target_id: str,
    action: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Handle match request.
    """
    if action.lower() == "like":
        send_match_request(db=db, target_id=target_id, current_user=current_user, profile_or_offer_id=None)
        message = "You liked the job!"
    elif action.lower() == "dislike":
        message = "You disliked the job!"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return {"message": message}

@match_web_router.get("/view-matches", response_class=HTMLResponse)
async def view_matches_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    matches = view_matches(db=db, current_user=current_user)
    return templates.TemplateResponse(
        "matches.html",
        {"request": request, "matches": matches},
    )