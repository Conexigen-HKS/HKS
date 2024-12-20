from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

#NOTE : Status - ACTIVE/BUSY. IF BUSY - COMPANIES CAN'T SEE JOB_APPLICATIONS FROM THIS PROFESSIONAL.

class ProfessionalResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    location: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    status: Optional[str]  # ACTIVE/BUSY
    summary: Optional[str]
    is_approved: bool
    picture: Optional[str]
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_orm(cls, professional):
        return cls(
            id=professional.id,
            first_name=professional.first_name,
            last_name=professional.last_name,
            location=professional.location.city_name if professional.location else None,
            phone=professional.phone,
            email=professional.email,
            website=professional.website,
            status=professional.status,
            summary=professional.summary,
            is_approved=professional.is_approved,
            picture=professional.picture,
            user_id=professional.user_id,
        )


class ProfessionalOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    location_name: str
    phone: str
    email: str
    website: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ProfessionalUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    picture: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReturnProfessional(BaseModel):
    id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    picture: Optional[str] = None


class ProfessionalOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    picture: Optional[str] = None
    status: Optional[str] = None
    is_approved: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator('location', mode='before')
    def validate_location(cls, value):
        if value:
            return value.city_name
        return None
