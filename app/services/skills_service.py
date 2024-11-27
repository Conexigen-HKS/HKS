from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from HKS.data.models import ProfessionalProfileSkills, Skills
from HKS.data.queries import create_skill, get_skills_for_profile
from HKS.data.schemas.skills import SkillCreate, SkillAssignment


def create_skill_service(db: Session, skill_data: SkillCreate):
    return create_skill(db, skill_data.name)


def assign_skill_to_job_application_service(db: Session, job_application_id: UUID, skill_data: SkillAssignment):
    # Check if the skill exists
    skill = db.query(Skills).filter(Skills.name == skill_data.name).first()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill with name '{skill_data.name}' not found.")

    # Prevent duplicate assignment
    existing_assignment = db.query(ProfessionalProfileSkills).filter(
        ProfessionalProfileSkills.professional_profile_id == job_application_id,
        ProfessionalProfileSkills.skills_id == skill.id
    ).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Skill already assigned to this job application.")

    # Assign the skill
    new_assignment = ProfessionalProfileSkills(
        professional_profile_id=job_application_id,  # Change to job application ID
        skills_id=skill.id,
        level=skill_data.level
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

def get_profile_skills_service(db: Session, profile_id: UUID):
    skill_links = get_skills_for_profile(db, profile_id)
    return [
        {
            "skill_id": link.skills_id,
            "name": skill.name,
            "level": link.level
        }
        for link, skill in skill_links
    ]
