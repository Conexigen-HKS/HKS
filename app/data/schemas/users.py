"""
Pydantic schemas for the user model.
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator, Field

from app.data.schemas.company import CompanyOut
from app.data.schemas.professional import ProfessionalOut


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    role: Literal["professional", "company"]

    model_config = ConfigDict(from_attributes=True)


class WaitingApproval(BaseModel):
    professionals: list[ProfessionalOut]
    companies: list[CompanyOut]


class ProfessionalRegister(BaseModel):
    username: str = Field(
        ..., description="Username of the user", min_length=3, max_length=20
    )
    password: str = Field(
        ..., description="Password of the user", min_length=6, max_length=20
    )
    first_name: str = Field(..., min_length=2, max_length=20)
    last_name: str = Field(..., min_length=3, max_length=20)
    location: str = Field(
        ..., description="City where the user is located", min_length=3, max_length=50
    )
    phone: Optional[str] = Field(
        None, description="Phone number of the user", min_length=8, max_length=15
    )
    email: Optional[str] = Field(
        None, description="Email address of the user", min_length=5, max_length=100
    )
    website: Optional[str] = Field(
        None, description="Website of the user or company", min_length=5, max_length=255
    )
    summary: str = Field(
        ..., description="Summary of the user", min_length=10, max_length=200
    )

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str):
        if value is None or value == "":
            return None
        if (
            any(c.islower() for c in value)
            and any(c.isupper() for c in value)
            and any(c.isdigit() for c in value)
            and any(c in "%*@$!?" for c in value)
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter,\
            one uppercase letter, one digit, and one special character."
        )


class CompanyRegister(BaseModel):
    username: str = Field(
        ..., description="Username of the company user", min_length=3, max_length=20
    )
    password: str = Field(..., min_length=6, max_length=20)
    company_name: str = Field(
        ..., description="Name of the company", min_length=3, max_length=50
    )
    description: str = Field(
        ..., description="Description of the company", min_length=10, max_length=200
    )
    location: str = Field(
        ...,
        description="City where the company is located",
        min_length=3,
        max_length=50,
    )
    phone: Optional[str] = Field(
        None, description="Phone number of the company", min_length=8, max_length=15
    )
    email: Optional[str] = Field(
        None, description="Email address of the company", min_length=5, max_length=100
    )
    website: Optional[str] = Field(
        None, description="Website of the company", min_length=5, max_length=255
    )

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str):
        if value is None or value == "":
            return None
        if (
            any(c.islower() for c in value)
            and any(c.isupper() for c in value)
            and any(c.isdigit() for c in value)
            and any(c in "%*@$!?" for c in value)
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter,\
            one uppercase letter, one digit, and one special character."
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
