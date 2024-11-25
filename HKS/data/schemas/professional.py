from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import List, Literal, Optional


class JobApplicationCreate(BaseModel):
    description: str
    min_salary: Optional[int]
    max_salary: Optional[int]
    status: Literal["active", "hidden", "private"]


class JobApplicationResponse(BaseModel):
    id: UUID
    description: str
    min_salary: Optional[int]
    max_salary: Optional[int]
    status: Literal["active", "hidden", "private", "matched"]
    skills: List[str]
    match_requests: List[UUID]

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