from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import Optional



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



from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


class ContactDetails(BaseModel):
    email: Optional[str]
    phone_number: Optional[str]
    web_page: Optional[str]
    linkedin: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CompanyAdModel(BaseModel):
    company_ad_id: Optional[UUID]
    position_title: str
    min_salary: float
    max_salary: float
    description: str
    location: str
    status: str
    contacts: Optional[ContactDetails]

    model_config = ConfigDict(from_attributes=True)


class CompanyAdModel2(BaseModel):
    position_title: Optional[str]
    min_salary: Optional[float]
    max_salary: Optional[float]
    description: Optional[str]
    location: Optional[str]
    status: Optional[str]
    contacts: Optional[ContactDetails]

    model_config = ConfigDict(from_attributes=True)