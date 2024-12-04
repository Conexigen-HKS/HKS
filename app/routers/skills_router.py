from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import ProfessionalProfile, User, Professional, ProfessionalProfileSkills
from app.data.schemas.skills import SkillCreate, SkillResponse
from app.services.skills_service import create_skill_service, get_profile_skills_service

skills_router = APIRouter(prefix="/skills", tags=["Skills"])

@skills_router.post("/", response_model=SkillResponse)
def create_skill_endpoint(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):
    skill = create_skill_service(db, skill_data)
    return SkillResponse(skill_id=skill.id, name=skill.name, level=None)


@skills_router.get("/profile/{profile_id}", response_model=list[SkillResponse])
def get_profile_skills(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    skills = get_profile_skills_service(db, profile_id)
    return [SkillResponse(**skill) for skill in skills]


