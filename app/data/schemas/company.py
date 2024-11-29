from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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

class CompanyInfoRequestModel(BaseModel):
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
    company_ad_id: UUID
    title: str
    min_salary: int
    max_salary: int
    description: str
    location: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    location: Optional[str]
    description: Optional[str]
    contacts: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    is_approved: bool
    username: str
    user_id: UUID

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
    title: Optional[str]
    min_salary: Optional[float]
    max_salary: Optional[float]
    description: Optional[str]
    location: Optional[str]
    status: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class CreateCompanyAdModel(BaseModel):
    company_name: str
    title: str
    min_salary: int
    max_salary: int
    description: str
    location: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class CompanyAdUpdateModel(BaseModel):
    title: Optional[str] = Field(None, example="Your title position here")
    min_salary: Optional[int] = Field(None, example=1111)
    max_salary: Optional[int] = Field(None, example=5555)
    description: Optional[str] = Field(None, example="Description for the position")
    location: Optional[str] = Field(None, example="Your location")
    status: Optional[str] = Field(None, example="active or closed/archived")

    class Config:
        orm_mode = True