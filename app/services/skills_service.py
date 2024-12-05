from uuid import UUID

from pydantic import UUID4
from sqlalchemy.orm import Session

from app.data.models import ProfessionalProfileSkills, Skills
from app.data.schemas.skills import SkillCreate


def create_skill(db: Session, name: str) -> Skills:
    existing_skill = db.query(Skills).filter(Skills.name == name).first()
    if existing_skill:
        return existing_skill
    skill = Skills(name=name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_skill_by_id(db: Session, skill_id: UUID) -> Skills:
    return db.query(Skills).filter(Skills.id == skill_id).first()


def get_skill_by_name(db: Session, name: str) -> Skills:
    return db.query(Skills).filter(Skills.name == name).first()


def get_skills_for_profile(db: Session, profile_id: UUID):
    return db.query(ProfessionalProfileSkills, Skills).join(Skills).filter(
        ProfessionalProfileSkills.professional_profile_id == profile_id
    ).all()


def create_skill_service(db: Session, skill_data: SkillCreate):
    return create_skill(db, skill_data.name)


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


def associate_skills_with_profile(db: Session, profile_id: UUID, skills: list[SkillCreate]):
    for skill_data in skills:
        skill = get_skill_by_name(db, skill_data.name)
        if not skill:
            skill = create_skill(db, skill_data.name)

        skill_assignment = ProfessionalProfileSkills(
            professional_profile_id=profile_id,
            skills_id=skill.id,
            level=skill_data.level
        )
        db.add(skill_assignment)
    db.commit()
