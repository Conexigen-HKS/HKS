from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Literal, Optional



class ProfessionalResponse(BaseModel):
    id: UUID #tova go nqmashe
    first_name: str
    last_name: str
    address: str
    status: Optional[str]
    summary: Optional[str]
    is_approved: bool
    # username: str
    user_id: UUID #promeneno na uuid ot str

    model_config = ConfigDict(from_attributes=True)

class SkillAssign(BaseModel):
    skill_id: UUID
    level: Optional[int] = Field(None, ge=1, le=10, description="Skill level from 1 to 10")

class ProfessionalOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    address: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ProfessionalUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[str]
    status: Optional[str]
    summary: Optional[str]
    picture: Optional[str]