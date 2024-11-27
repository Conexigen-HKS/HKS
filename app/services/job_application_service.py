from http.client import HTTPException
from typing import Optional
from uuid import UUID

from pydantic import UUID4
from sqlalchemy.orm import Session

from HKS.data.models import ProfessionalProfile, CompanyOffers, ProfessionalProfileSkills, Skills, RequestsAndMatches
from HKS.data.schemas.job_application import JobApplicationCreate

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
