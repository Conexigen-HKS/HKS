from typing import Optional
#uvicorn app.main:app --reload
from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.common.auth import get_current_user
from app.data.database import Session, get_db
from app.data.models import ProfessionalProfile, User
from app.routers.company_ad_router import company_ad_router
from app.routers.company_router import company_router
from app.routers.job_app_router import job_app_router
from app.routers.location_router import locations_router
from app.routers.professional_router import professional_router
from app.routers.skills_router import skills_router
from app.routers.user_router import users_router
from app.routers.admin_router import admin_router
from app.routers.message_router import messages_router
from app.routers.match_router import match_router
from app.routers.skills_router import skills_router
from app.routers_web.job_search_router import job_search_router
from app.routers_web.message_router_web import message_router_web

import uvicorn

from app.routers_web.company_router import company_router_web
from app.routers_web.job_ad_router import job_ad_router
from app.routers_web.job_app_router import job_app_router_web
from app.routers_web.mathing_router import match_web_router
from app.routers_web.professional_router import professional_router_web

from app.routers_web.user_router import users_router_web
from app.services.company_ad_service import get_spotlight_job_ad, get_recent_job_ads
from app.services.job_app_service import get_recent_applications, get_spotlight_application

app = FastAPI()
app.include_router(admin_router)
app.include_router(job_ad_router)
app.include_router(messages_router)
app.include_router(match_router)
app.include_router(company_router)
app.include_router(company_ad_router)
app.include_router(users_router)
app.include_router(locations_router)
app.include_router(skills_router)
app.include_router(users_router_web)
app.include_router(company_router_web)
app.include_router(professional_router_web)
app.include_router(job_app_router_web)
app.include_router(job_search_router, prefix="/job_search")
app.include_router(message_router_web)


app.include_router(match_web_router)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),  # Handles unauthenticated users
):
    # Fetch recent job applications, spotlight application, recent job ads, and spotlight job ad
    recent_applications = get_recent_applications(db, limit=3)
    spotlight_application = get_spotlight_application(db)
    recent_job_ads = get_recent_job_ads(db, limit=4)
    spotlight_job_ad = get_spotlight_job_ad(db)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": current_user,  # None if not logged in
            "recent_applications": recent_applications,
            "spotlight_application": spotlight_application,
            "recent_job_ads": recent_job_ads,
            "spotlight_job_ad": spotlight_job_ad,
        },
    )



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

