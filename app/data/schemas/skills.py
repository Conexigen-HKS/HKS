from pydantic import BaseModel, UUID4


class SkillCreate(BaseModel):
    name: str

class SkillAssignment(BaseModel):
    skill_id: UUID4
    level: int
class ProfessionalSkillResponse(BaseModel):
    professional_profile_id: UUID4
    skill_id: UUID4
    name: str
    level: int

class SkillResponse(BaseModel):
    skill_id: UUID4
    name: str
    level: int
