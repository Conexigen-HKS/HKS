from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime


class CompanyOfferBase(BaseModel):
    min_salary: int
    max_salary: int
    location: str
    description: Optional[str] = None


class CompanyOfferCreate(CompanyOfferBase):
    requirements: Optional[List[dict]] = []


class ProfessionalApplicationCreate(BaseModel):
    min_salary: int
    max_salary: int
    location: str
    description: str


class CompanyOfferResponse(BaseModel):
    id: UUID4
    type: str
    status: str
    min_salary: int
    max_salary: int
    location: str
    description: Optional[str]
    created_at: datetime
    requirements: Optional[List[dict]] = None

    class Config:
        orm_mode = True
