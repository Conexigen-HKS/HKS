from http.client import HTTPException
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data.models import ProfessionalProfile, ProfessionalProfileSkills, Skills, RequestsAndMatches, CompanyOffers


def create_job_application(db: Session, professional_id: str, min_salary: int, max_salary: int, location_id: UUID, description: str):
    job_application = ProfessionalProfile(
        professional_id=professional_id,
        min_salary=min_salary,
        max_salary=max_salary,
        location_id=location_id,
        description=description,
        status="open"
    )
    db.add(job_application)
    db.commit()
    db.refresh(job_application)
    return job_application



def assign_skill_to_job_application_by_name(
    db: Session,
    job_application_id: UUID,
    skill_name: str,
    level: Optional[int] = None
):
    skill = db.query(Skills).filter(Skills.name == skill_name).first()
    if not skill:
        skill = Skills(name=skill_name)
        db.add(skill)
        db.commit()
        db.refresh(skill)

    existing_assignment = db.query(ProfessionalProfileSkills).filter(
        ProfessionalProfileSkills.professional_profile_id == job_application_id,
        ProfessionalProfileSkills.skills_id == skill.id
    ).first()

    if existing_assignment:
        raise HTTPException(status_code=400, detail="Skill is already assigned to this job application")

    skill_assignment = ProfessionalProfileSkills(
        professional_profile_id=job_application_id,
        skills_id=skill.id,
        level=level
    )
    db.add(skill_assignment)
    db.commit()
    return skill_assignment


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



def get_all_job_applications_service(db: Session, professional_id: UUID):
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
            "location_name": app.location.name if app.location else None,
            "skills": [s.skill.name for s in app.skills],
        }
        for app in applications
    ]

def search_job_ads_service(db: Session, query: Optional[str] = None, location: Optional[str] = None):
    job_ads = db.query(CompanyOffers).filter(CompanyOffers.status == "active")

    if query:
        job_ads = job_ads.filter(CompanyOffers.description.ilike(f"%{query}%"))
    if location:
        job_ads = job_ads.filter(CompanyOffers.location.ilike(f"%{location}%"))

    return [
        {
            "id": ad.id,
            "description": ad.description,
            "min_salary": ad.min_salary,
            "max_salary": ad.max_salary,
            "location": ad.location,
        }
        for ad in job_ads.all()
    ]