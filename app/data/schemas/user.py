import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from data.schemas.professional import ProfessionalOut, ProfessionalResponse
from data.schemas.company import CompanyOut, CompanyResponse


class UserResponse(BaseModel):
    id: UUID
    username: str
    is_admin: bool
    role: str
    created_at: datetime
    professional: Optional[ProfessionalResponse]
    company: Optional[CompanyResponse]

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    id: UUID | None = None
    username: str 

    @classmethod
    def from_query_result(cls, id, username):
        return cls(
            id=id,
            username=username)
    
class WaitingApproval(BaseModel):
    professionals: list[ProfessionalOut]
    companies: list[CompanyOut]
    

