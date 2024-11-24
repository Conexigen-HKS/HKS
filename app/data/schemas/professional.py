from pydantic import BaseModel
from uuid import UUID

class ProfessionalUpgrade(BaseModel):
    first_name: str
    last_name: str
    address: str
    summary: str


class ProfessionalResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    address: str
    summary: str
    status: str
    is_approved: bool
