import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from HKS.common.auth import get_current_user
from HKS.services.skills_service import assign_skill_to_profile_service, get_profile_skills_service, \
    create_skill_service
from app.data.database import get_db
from app.data.models import ProfessionalProfile, User, Professional, Skills
from app.data.schemas.skills import SkillCreate, SkillAssignment, ProfessionalSkillResponse, SkillResponse

skills_router = APIRouter(prefix="/skills", tags=["Skills"])

@skills_router.post("/", response_model=SkillResponse)
def create_skill(skill_data: SkillCreate, db: Session = Depends(get_db)):
    skill = create_skill_service(db, skill_data)
    return SkillResponse(
        skill_id=skill.id,
        name=skill.name,
        level=0
    )

@skills_router.post("/assign", response_model=ProfessionalSkillResponse)
def assign_skill_to_professional(skill_data: SkillAssignment, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    professional = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    professional_profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == professional.id
    ).first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found.")

    assigned_skill = assign_skill_to_profile_service(
        db=db,
        profile_id=professional_profile.id,
        skill_data=skill_data
    )

    skill = db.query(Skills).filter(Skills.id == assigned_skill.skills_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found.")

    return ProfessionalSkillResponse(
        professional_profile_id=assigned_skill.professional_profile_id,
        skill_id=assigned_skill.skills_id,
        name=skill.name,
        level=assigned_skill.level
    )

#TODO: DELETE SKILL FROM ADMIN
#TODO: DELETE JOB APPLICATION FROM ADMIN OR MAKE IT INVISIBLE
#ALMOST DONE: JOB APPLICATION CREATE
#DONE: ADD SKILL TO PROFESSIONAL (GET ID OF PROFESSIONAL BY FORIGN KEY IN USER)
#TODO: PHOTOS OF PROFESSIONAL
#IF BREAKS SOMETHING CASCADE USE ->   professional = relationship("Professional", back_populates="user", uselist=False, cascade="all, delete-orphan")




@skills_router.get("/{profile_id}", response_model=list[ProfessionalSkillResponse])
def get_skills_for_profile(profile_id: UUID, db: Session = Depends(get_db)):
    return get_profile_skills_service(db, profile_id)
