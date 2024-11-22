from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID

class ProfessionalRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    address: str
    summary: str
    city: str
    picture: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ProfessionalResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    address: str
    city: str
    status: str
    summary: Optional[str]
    picture: Optional[str]
    user_id: UUID
    is_approved: bool
    number_of_matches: int
    number_of_active_applications: int

    model_config = ConfigDict(from_attributes=True)

