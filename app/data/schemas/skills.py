from typing import Optional

from pydantic import BaseModel, UUID4, root_validator, model_validator


class SkillCreate(BaseModel):
    name: str  # Skill name
    level: Optional[str] = None  # Optional skill level

class SkillResponse(BaseModel):
    skill_id: UUID4
    name: str
    level: str