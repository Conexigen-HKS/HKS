from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class ProfessionalResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    location: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    status: Optional[str]
    summary: Optional[str]
    is_approved: bool
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, professional):
        return cls(
            id=professional.id,
            first_name=professional.first_name,
            last_name=professional.last_name,
            location=professional.location.name if professional.location else None,
            phone=professional.phone,
            email=professional.email,
            website=professional.website,
            status=professional.status,
            summary=professional.summary,
            is_approved=professional.is_approved,
            user_id=professional.user_id
        )

class ProfessionalOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    location: str
    phone: str
    email: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)
