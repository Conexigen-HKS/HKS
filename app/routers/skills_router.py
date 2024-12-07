"""
This module contains the FastAPI router for the skills endpoints.
In this file, we define the routes for the skills service. We have two endpoints:
- create_skill_endpoint: This endpoint is used to create a new skill.
- get_profile_skills: This endpoint is used to get all skills of a profile.
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.data.schemas.skills import SkillCreate, SkillResponse
from app.services.skills_service import (
    create_skill_service,
    get_profile_skills_service,
)

skills_router = APIRouter(prefix="/api/skills", tags=["Skills"])


@skills_router.post("/", response_model=SkillResponse)
def create_skill_endpoint(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new skill
    Accepts a skill data object and a database session and returns a skill response.
    """
    skill = create_skill_service(db, skill_data)
    return SkillResponse(skill_id=skill.id, name=skill.name, level=None)


@skills_router.get("/profile/{profile_id}", response_model=list[SkillResponse])
def get_profile_skills(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all skills of a profile
    Accepts a profile id and a database session and returns a list of skill responses.
    """
    skills = get_profile_skills_service(db, profile_id)
    return [SkillResponse(**skill) for skill in skills]
