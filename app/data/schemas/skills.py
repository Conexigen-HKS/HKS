from typing import Optional

from pydantic import BaseModel, UUID4


class SkillCreate(BaseModel):
    name: str
    level: Optional[str] = None


class SkillResponse(BaseModel):
    skill_id: UUID4
    name: str
    level: Optional[str]
