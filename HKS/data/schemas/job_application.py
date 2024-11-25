from pydantic import BaseModel, UUID4
from typing import Optional

class JobApplicationCreate(BaseModel):
    description: str
    min_salary: int
    max_salary: int
    status: str
    location_id: Optional[UUID4]


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
