from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import ProfessionalProfile, User, Professional, ProfessionalProfileSkills
from app.data.schemas.skills import SkillCreate, SkillResponse
from app.services.skills_service import create_skill_service

skills_router = APIRouter(prefix="/skills", tags=["Skills"])

@skills_router.post("/", response_model=SkillResponse)
def create_skill(skill_data: SkillCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    #
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Only admins can create skills.")

    skill = create_skill_service(db, skill_data)
    return SkillResponse(
        skill_id=skill.id,
        name=skill.name,
        level=0
    )


#TODO: DELETE SKILL FROM ADMIN
#TODO: DELETE JOB APPLICATION FROM ADMIN OR MAKE IT INVISIBLE
#DONE: JOB APPLICATION CREATE
#DONE: ADD SKILL TO PROFESSIONAL (GET ID OF PROFESSIONAL BY FORIGN KEY IN USER)
#TODO: PHOTOS OF PROFESSIONAL
#IF BREAKS SOMETHING CASCADE USE ->   professional = relationship("Professional", back_populates="user", uselist=False, cascade="all, delete-orphan")


@skills_router.get("/job_application/{job_application_id}/skills", response_model=list[SkillResponse])
def get_skills_for_job_application(job_application_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    professional = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    job_application = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == job_application_id).first()

    if not job_application or (job_application.professional_id != professional.id and not current_user.is_admin):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view skills for this job application."
        )

    skill_links = db.query(ProfessionalProfileSkills).filter(
        ProfessionalProfileSkills.professional_profile_id == job_application_id
    ).all()
    return [
        SkillResponse(skill_id=link.skills_id, name=link.skill.name, level=link.level)
        for link in skill_links
    ]