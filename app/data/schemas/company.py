from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyInfoModel(BaseModel):
    company_name: str
    company_description: str
    company_location: str
    company_contacts: str
    company_logo: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    company_active_job_ads: Optional[list | int]

    model_config = ConfigDict(from_attributes=True)


class CompanyAdModel(BaseModel):
    company_name: str
    company_ad_id: str | None = None
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: Optional[str]
    status: str

    model_config = ConfigDict(from_attributes=True)


class ShowCompanyModel(BaseModel):
    company_name: str
    company_description: str
    company_location: str
    company_contacts: str
    company_phone: Optional[str]
    company_email: Optional[str]
    company_website: Optional[str]
    company_logo: Optional[str]
    company_active_job_ads: List[CompanyAdModel]


    model_config = ConfigDict(from_attributes=True)


class CompanyOut(BaseModel):
    id: UUID
    name: str
    address: str
    description: str
    contacts: str
    phone: str
    email: str
    website: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class CompanyAdModel2(BaseModel):
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: str
    status: str

    model_config = ConfigDict(from_attributes=True)