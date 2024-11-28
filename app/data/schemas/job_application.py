from pydantic import BaseModel, UUID4
from typing import Optional, List

from app.data.schemas.skills import SkillCreate


class JobApplicationCreate(BaseModel):
    description: str
    min_salary: int
    max_salary: int
    status: str
    # location_id: Optional[int] = None
    city_name: Optional[str] = None #primenuvano ot location_name
    skills: List[SkillCreate]

class JobApplicationResponse(BaseModel):
    id: UUID4
    description: str
    min_salary: int
    max_salary: int
    status: str
    location_name: Optional[str]
    skills: list[str]

    class Config:
        orm_mode = True