"""
Skills service module
In this module, we define the skills service functions. We have the following functions:
- create_skill: This function is used to create a new skill.
- get_skill_by_id: This function is used to get a skill by its ID.
- get_skill_by_name: This function is used to get a skill by its name.
- get_skills_for_profile: This function is used to get skills for a profile.
- create_skill_service: This function is used to create a skill.
- get_profile_skills_service: This function is used to get profile skills.
- associate_skills_with_profile: This function is used to associate skills with a profile.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from app.data.models import ProfessionalProfileSkills, Skills
from app.data.schemas.skills import SkillCreate


def create_skill(db: Session, name: str) -> Skills:
    """
    Create a new skill
    :param db: Database session
    :param name: Skill name
    :return: New skill
    """
    existing_skill = db.query(Skills).filter(Skills.name == name).first()
    if existing_skill:
        return existing_skill
    skill = Skills(name=name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_skill_by_id(db: Session, skill_id: UUID) -> Skills:
    """
    Get a skill by its ID
    :param db: Database session
    :param skill_id: Skill ID
    :return: Skill
    """
    return db.query(Skills).filter(Skills.id == skill_id).first()


def get_skill_by_name(db: Session, name: str) -> Skills:
    """
    Get a skill by its name
    :param db: Database session
    :param name: Skill name
    :return: Skill
    """
    return db.query(Skills).filter(Skills.name == name).first()


def get_skills_for_profile(db: Session, profile_id: UUID):
    """
    Get skills for a profile
    :param db: Database session
    :param profile_id: Profile ID
    :return: List of skills
    """
    return db.query(ProfessionalProfileSkills, Skills).join(Skills).filter(
        ProfessionalProfileSkills.professional_profile_id == profile_id
    ).all()


def create_skill_service(db: Session, skill_data: SkillCreate):
    """
    Create a skill
    :param db: Database session
    :param skill_data: Skill data
    :return: Skill
    """
    return create_skill(db, skill_data.name)


def get_profile_skills_service(db: Session, profile_id: UUID):
    """
    Get profile skills
    :param db: Database session
    :param profile_id: Profile ID
    :return: List of skills
    """
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
    """
    Associate skills with a profile
    :param db: Database session
    :param profile_id: Profile ID
    :param skills: List of skills
    """
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
