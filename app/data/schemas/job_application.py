"""
Pydantic schemas for job applications.
"""
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field, model_validator

# TODO да направя един валидатор за статусите на апликациите, active/hidden/private и тн.
from app.data.schemas.skills import SkillResponse


class SkillCreate(BaseModel):
    name: str
    level: int


class JobApplicationCreate(BaseModel):
    description: str
    min_salary: int
    max_salary: int
    status: str
    city_name: Optional[str] = None
    skills: List[SkillCreate]


class JobApplicationResponse(BaseModel):
    user_id: UUID4
    id: UUID4
    description: str
    min_salary: int
    max_salary: int
    status: str
    location_name: Optional[str]
    skills: List[SkillResponse]


class JobApplicationEdit(BaseModel):
    description: Optional[str] = Field(
        None,
        example="Description of the job position",
        description="Job position description.",
    )
    min_salary: Optional[int] = Field(
        None, example=1000, ge=0, description="Minimum salary for the position."
    )
    max_salary: Optional[int] = Field(
        None, example=1500, ge=0, description="Maximum salary for the position."
    )
    status: Optional[str] = Field(
        None, example="active", description="Status of the job application."
    )
    location: Optional[str] = Field(
        None, example="Sofia", description="Location of the job position."
    )
    skills: Optional[List[SkillCreate]] = None

    @model_validator(mode="after")
    def check_salary_range(cls, values):
        min_salary = values.min_salary
        max_salary = values.max_salary

        if min_salary is not None and max_salary is not None:
            if max_salary < min_salary:
                raise ValueError(
                    "max_salary must be greater than or equal to min_salary."
                )

        if min_salary is not None and max_salary is None:
            raise ValueError("max_salary is required when min_salary is provided.")

        if max_salary is not None and min_salary is None:
            raise ValueError("min_salary is required when max_salary is provided.")

        return values

    model_config = ConfigDict(
        from_attributes=True,
        schema_extra={
            "example": {
                "description": "Updated job description",
                "min_salary": 5000,
                "max_salary": 10000,
                "status": "active",
                "city_name": "Sofia",
                "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "SQL"}],
            }
        },
    )
