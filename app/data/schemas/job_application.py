from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class JobApplicationCreate(BaseModel):
    desired_salary_range: Optional[str]
    description: Optional[str]
    location: str
    status: str
    skills: List[str]


class JobApplicationResponse(BaseModel):
    id: UUID
    desired_salary_range: Optional[str]
    description: Optional[str]
    location: str
    status: str

    class Config:
        orm_mode = True


class SearchJobAds(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    skills: List[str] = []
