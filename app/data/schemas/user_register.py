from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
from data.schemas.professional import ProfessionalOut, ProfessionalResponse
from data.schemas.company import CompanyOut, CompanyResponse


class UserResponse(BaseModel):
    username: str
    role: str
    created_at: datetime
    professional: Optional[ProfessionalResponse]
    company: Optional[CompanyResponse]

    model_config = ConfigDict(from_attributes=True)


class BaseUser(BaseModel):
    username: str
    hashed_password: str
    role: Literal['professional', 'company']


class WaitingApproval(BaseModel):
    professionals: list[ProfessionalOut]
    companies: list[CompanyOut]


class ProfessionalRegister(BaseModel):
    username: str = Field(..., description="Username of the user", min_length=3, max_length=20)
    password: str = Field(..., description="Password of the user", min_length=6, max_length=20)
    first_name: str = Field(..., min_length=2, max_length=20)
    last_name: str = Field(..., min_length=3, max_length=20)
    address: str = Field(..., description="Address of the user", min_length=3, max_length=50)
    summary: str = Field(..., description="Summary of the user", min_length=10, max_length=200)

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, value: str):
        if value is None or value == '':
            return None
        if (
            any(c.islower() for c in value) and
            any(c.isupper() for c in value) and
            any(c.isdigit() for c in value) and
            any(c in "%*@$!?" for c in value)
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.")


class CompanyRegister(BaseModel):
    username: str = Field(..., description="Username of the company user", min_length=3, max_length=20)
    password: str = Field(...,min_length=6, max_length=20)
    company_name: str = Field(..., description="Name of the company", min_length=3, max_length=50)
    description: str = Field(..., description="Description of the company", min_length=10, max_length=200)
    address: str = Field(..., description="Address of the company", min_length=3, max_length=50)

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, value: str):
        if value is None or value == '':
            return None
        if (
            any(c.islower() for c in value) and
            any(c.isupper() for c in value) and
            any(c.isdigit() for c in value) and
            any(c in "%*@$!?" for c in value)
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.")