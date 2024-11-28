from typing import Optional

from pydantic import BaseModel, UUID4, root_validator, model_validator


class SkillCreate(BaseModel):
    name: str

class SkillAssignment(BaseModel):
    name: Optional[str]
    level: int

    @model_validator(mode="before")
    @classmethod
    def validate_skill_input(cls, values):
        """
        Ensure that `name` is provided.
        """
        name = values.get("name")

        if not name:
            raise ValueError("The 'name' field is required to assign a skill.")
        return values
class ProfessionalSkillResponse(BaseModel):
    professional_profile_id: UUID4
    skill_id: UUID4
    name: str
    level: int

class SkillResponse(BaseModel):
    skill_id: UUID4
    name: str
    level: int
