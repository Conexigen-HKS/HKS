
from http.client import HTTPException
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.data.models import ProfessionalProfile, ProfessionalProfileSkills, Skills, RequestsAndMatches, CompanyOffers, \
    Location
from app.data.schemas.job_application import JobApplicationResponse
from app.data.schemas.skills import SkillCreate

#WORKS
def create_job_application(
    db: Session,
    professional_id: str,
    user_id: str,
    description: str,
    min_salary: int,
    max_salary: int,
    city_name: str,
    status: str,
    skills: List[SkillCreate]
):
    location = db.query(Location).filter(Location.city_name == city_name).first()
    if not location:
        raise HTTPException(status_code=400, detail=f"Location '{city_name}' does not exist.")


    job_application = ProfessionalProfile(
        professional_id=professional_id,
        user_id=user_id,
        description=description,
        min_salary=min_salary,
        max_salary=max_salary,
        location_id=location.id,
        status=status
    )
    db.add(job_application)
    db.commit()
    db.refresh(job_application)

    for skill_data in skills:
        skill = db.query(Skills).filter(Skills.name == skill_data.name).first()
        if not skill:
            skill = Skills(name=skill_data.name)
            db.add(skill)
            db.commit()
            db.refresh(skill)

        skill_assignment = ProfessionalProfileSkills(
            professional_profile_id=job_application.id,
            skills_id=skill.id,
            level=skill_data.level
        )
        db.add(skill_assignment)

    db.commit()
    return job_application



#WORKS
def get_job_application(db: Session, job_application_id: UUID):
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == job_application_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Job application not found")

    matches = db.query(RequestsAndMatches.company_offers_id).filter(
        RequestsAndMatches.professional_profile_id == job_application_id
    ).all()
    return profile, [match.company_offers_id for match in matches]


def set_main_job_application_service(db: Session, job_application_id: UUID, professional_id: UUID):
    application = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == job_application_id,
        ProfessionalProfile.professional_id == professional_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional_id
    ).update({"chosen_company_offer_id": None})

    application.chosen_company_offer_id = application.id
    db.commit()
    return application


#WORKS
def get_all_job_applications_service(db: Session, professional_id: UUID) -> List[JobApplicationResponse]:
    applications = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional_id
    ).all()

    return [
        {
            "id": app.id,
            "description": app.description,
            "min_salary": app.min_salary,
            "max_salary": app.max_salary,
            "status": app.status,
            "location_name": app.location.city_name if app.location else None,
            "skills": [s.skill.name for s in app.skills],
        }
        for app in applications
    ]

# def search_job_ads_service(db: Session, query: Optional[str] = None, location: Optional[str] = None):
#     job_ads = db.query(CompanyOffers).filter(CompanyOffers.status == "active")
# #Here, CompanyOffers.location is a relationship to the Location model,
# #  not a direct column containing string data.
# #  Therefore, applying ilike on it is invalid.
#     if query:
#         job_ads = job_ads.filter(CompanyOffers.description.ilike(f"%{query}%"))
#     if location:
#         job_ads = job_ads.filter(CompanyOffers.location.ilike(f"%{location}%"))

#     return [
#         {
#             "id": ad.id,
#             "description": ad.description,
#             "min_salary": ad.min_salary,
#             "max_salary": ad.max_salary,
#             "location": ad.location,
#         }
#         for ad in job_ads.all()
    # ]

def search_job_ads_service(db: Session, query: Optional[str] = None, location: Optional[str] = None):
    job_ads_query = db.query(CompanyOffers).filter(CompanyOffers.status == "active")

    if query:
        job_ads_query = job_ads_query.filter(CompanyOffers.description.ilike(f"%{query}%"))
    
    if location:
        job_ads_query = job_ads_query.join(Location).filter(Location.city_name.ilike(f"%{location}%"))

    job_ads = job_ads_query.options(joinedload(CompanyOffers.location)).all()

    return [
        {
            "id": ad.id,
            "description": ad.description,
            "min_salary": ad.min_salary,
            "max_salary": ad.max_salary,
            "location": ad.location.city_name if ad.location else "N/A",
            "status": ad.status
        }
        for ad in job_ads
    ]

def get_archived_job_applications_service(db: Session):
    archived_job_apps = db.query(ProfessionalProfile).filter(ProfessionalProfile.status == "Matched").all()

    return [
        JobApplicationResponse(
            id=job_app.id,
            description=job_app.description,
            min_salary=job_app.min_salary,
            max_salary=job_app.max_salary,
            status=job_app.status,
            location_name=job_app.location.city_name if job_app.location else "N/A",
            skills=[skill.skill.name for skill in job_app.skills]
        )
        for job_app in archived_job_apps
    ]


def get_active_job_applications_service(db: Session):
    active_job_apps = db.query(ProfessionalProfile).filter(ProfessionalProfile.status == "Active").all()

    return [
        JobApplicationResponse(
            id=job_app.id,
            description=job_app.description,
            min_salary=job_app.min_salary,
            max_salary=job_app.max_salary,
            status=job_app.status,
            location_name=job_app.location.city_name if job_app.location else "N/A",
            skills=[skill.skill.name for skill in job_app.skills]
        )
        for job_app in active_job_apps
    ]


def search_job_applications_service(
        db: Session,
        query: Optional[str] = None,
        location: Optional[str] = None
):
    job_applications_query = db.query(ProfessionalProfile).filter(ProfessionalProfile.status == "Active")

    if query:
        job_applications_query = job_applications_query.filter(ProfessionalProfile.description.ilike(f"%{query}%"))
    if location:
        job_applications_query = job_applications_query.join(Location).filter(Location.city_name.ilike(f"%{location}%"))

    job_apps = job_applications_query.all()

    return [
        JobApplicationResponse(
            id=job_app.id,
            description=job_app.description,
            min_salary=job_app.min_salary,
            max_salary=job_app.max_salary,
            status=job_app.status,
            location_name=job_app.location.city_name if job_app.location else "N/A",
            skills=[skill.skill.name for skill in job_app.skills]
        )
        for job_app in job_apps
    ]

def view_job_application(db: Session, job_application_id: UUID, user_id: UUID):
    job_application = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == job_application_id,
        ProfessionalProfile.user_id == user_id
    ).first()
    if not job_application:
        raise HTTPException(status_code=404, detail="Job application not found")

    return JobApplicationResponse(
        id=job_application.id,
        description=job_application.description,
        min_salary=job_application.min_salary,
        max_salary=job_application.max_salary,
        status=job_application.status,
        location_name=job_application.location.city_name if job_application.location else None,
        skills=[s.skill.name for s in job_application.skills]
    )