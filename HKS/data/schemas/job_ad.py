from pydantic import BaseModel
from typing import Optional

from HKS.data.schemas.contacts import ContactDetails


class CompanyAdModel(BaseModel):
    company_ad_id: Optional[str]
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: str
    status: str
    contacts: Optional[ContactDetails]  # Nested model to add contact details


class CompanyAdModel2(BaseModel):
    position_title: Optional[str]
    min_salary: Optional[float]
    max_salary: Optional[float]
    description: Optional[str]
    location: Optional[str]
    status: Optional[str]
