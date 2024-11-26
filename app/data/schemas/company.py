from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: str
    description: Optional[str]
    contacts: Optional[str]
    is_approved: bool
    username: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ShowCompanyModel(BaseModel):
    company_name: str
    company_description: str
    company_address: str
    company_contacts: str
    company_logo: str
    company_active_job_ads: list


class CompanyInfoModel(BaseModel):
    # company_name: str
    company_description: str
    company_address: str
    company_contacts: str
    company_logo: str
    company_active_job_ads: list | int


class CompanyAdModel(BaseModel):
    company_ad_id: str | None = None
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: str
    status: str


class CompanyAdModel2(BaseModel):
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: str
    status: str