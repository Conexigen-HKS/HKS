from http.client import HTTPException
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import Location, ProfessionalProfile, Skills, User
from app.data.schemas.job_application import JobApplicationCreate, JobApplicationEdit
from app.data.schemas.skills import SkillCreate
from app.services.job_app_service import (
    create_job_application,
    delete_job_application,
    edit_job_app,
    get_all_job_applications_service,
    set_main_job_application_service,
    view_job_application,
)
from app.services.professional_service import get_own_job_applications

job_app_router_web = APIRouter(prefix="/job_applications", tags=["Job Applications"])
templates = Jinja2Templates(directory="app/templates")


@job_app_router_web.get('/search', response_class=HTMLResponse)
def search_job_applications(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    keyword: str = "",
    location: str = "",
    skill: str = "",
    min_salary: int = 0,
    max_salary: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Start with only Active applications
    query = db.query(ProfessionalProfile).filter(ProfessionalProfile.status == "Active")

    # Apply filters if provided
    if keyword:
        query = query.filter(ProfessionalProfile.description.ilike(f"%{keyword}%"))
    if location:
        query = query.join(Location).filter(Location.city_name.ilike(f"%{location}%"))
    if skill:
        query = query.join(ProfessionalProfile.skills).join(Skills).filter(Skills.name.ilike(f"%{skill}%"))
    if min_salary > 0 and max_salary > 0:
        query = query.filter(
            (ProfessionalProfile.min_salary >= min_salary) |
            (ProfessionalProfile.max_salary <= max_salary)
        )
    elif min_salary > 0:
        query = query.filter(ProfessionalProfile.min_salary >= min_salary)
    elif max_salary > 0:
        query = query.filter(ProfessionalProfile.max_salary <= max_salary)

    # Pagination
    job_apps = query.offset((page - 1) * per_page).limit(per_page).all()

    # Format data for the template
    job_apps_data = [
        {
            "id": app.id,
            "description": app.description,
            "location": app.location.city_name if app.location else "N/A",
            "min_salary": app.min_salary,
            "max_salary": app.max_salary,
            "skills": [skill.skill.name for skill in app.skills],
            "status": app.status,
        }
        for app in job_apps
    ]

    return templates.TemplateResponse(
        "listing_job_apps.html",
        {
            "request": request,
            "job_apps": job_apps_data,
            "current_page": page,
            "total_pages": (query.count() + per_page - 1) // per_page,
            "keyword": keyword,
            "location": location,
            "skill": skill,
            "min_salary": min_salary,
            "max_salary": max_salary,
        },
    )



@job_app_router_web.get("/", response_class=HTMLResponse)
def view_applications(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    applications = get_all_job_applications_service(db, professional_id=current_user.id)
    return templates.TemplateResponse("job_applications.html", {"request": request, "job_applications": applications})


@job_app_router_web.api_route("/create", methods=["GET", "POST"], response_class=HTMLResponse)
async def create_application(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if request.method == "GET":
        return templates.TemplateResponse("create_job_application.html", {"request": request})

    if request.method == "POST":
        form_data = await request.form()
        skills_input = form_data.getlist("skills[]")
        levels_input = form_data.getlist("levels[]")

        skills = [
            SkillCreate(name=skill, level=level)
            for skill, level in zip(skills_input, levels_input)
        ]

        # Create JobApplicationCreate object
        job_data = JobApplicationCreate(
            description=form_data.get("description"),
            min_salary=int(form_data.get("min_salary", 0)),
            max_salary=int(form_data.get("max_salary", 0)),
            status="Hidden",  # Set status to "Hidden" by default
            city_name=form_data.get("city_name"),
            skills=skills
        )
        create_job_application(db, current_user.id, job_data)
        return RedirectResponse("/", status_code=303)


@job_app_router_web.get("/edit/{job_id}", response_class=HTMLResponse)
def edit_application_page(job_id: UUID, request: Request, db: Session = Depends(get_db)):
    job = view_job_application(db, job_id)
    return templates.TemplateResponse("edit_job_application.html", {"request": request, "job": job})


@job_app_router_web.post("/job_applications/{job_id}")
def update_application(job_id: UUID, data: JobApplicationEdit, db: Session = Depends(get_db)):
    edit_job_app(job_id, data, db)
    return RedirectResponse("/", status_code=303)


@job_app_router_web.get("/delete/{job_id}")
def delete_application(job_id: UUID, db: Session = Depends(get_db)):
    delete_job_application(job_id, db)
    return RedirectResponse("/", status_code=303)

@job_app_router_web.get("/view-applications", response_class=HTMLResponse)
async def view_job_applications_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_applications = get_own_job_applications(db, current_user)
    return templates.TemplateResponse(
        "job_applications.html",
        {"request": request, "job_applications": job_applications},
    )

@job_app_router_web.get("/details/{job_id}", response_class=HTMLResponse)
def view_single_job_application(
    job_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View the details of a single job application.
    """
    # Fetch job application by ID
    application = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == job_id).first()

    if not application:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Job application not found."},
        )
    is_owner = application.user_id == current_user.id

    # Prepare data for rendering
    application_data = {
        "id": application.id,
        "title": application.description or "Untitled",
        "description": application.description,
        "location": application.location.city_name if application.location else "Unknown",
        "min_salary": application.min_salary,
        "max_salary": application.max_salary,
        "status": application.status,
        "picture": application.professional.picture,
        "professional_name": f"{application.professional.first_name} {application.professional.last_name}",
        "email": application.professional.email,
    }

    return templates.TemplateResponse(
        "job_app_single.html",
        {"request": request, "application": application_data, "is_owner": is_owner},
    )

@job_app_router_web.put("/archive/{application_id}")
def archive_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Archive a job application by setting its status to "Hidden".
    """
    application = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == application_id).first()

    if not application:
        raise HTTPException(status_code=404, detail="Job application not found.")

    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to archive this application.")

    # Update the status to "Hidden"
    application.status = "Hidden"
    db.commit()

    return {"message": "Job application archived successfully."}


@job_app_router_web.put("/set-main/{job_application_id}")
def set_main_application(
    job_application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set a specific job application as the main one by updating its status to "Active".
    Other applications will be set to "Hidden".
    """
    response = set_main_job_application_service(db, job_application_id, current_user)
    return response