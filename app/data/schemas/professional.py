from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class ProfessionalProfileBase(BaseModel):
    description: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    status: str


class ProfessionalProfileCreate(ProfessionalProfileBase):
    pass


class ProfessionalProfileUpdate(ProfessionalProfileBase):
    pass


class ProfessionalProfileResponse(ProfessionalProfileBase):
    id: UUID
    user_id: UUID
    professional_id: UUID
    chosen_company_offer_id: Optional[UUID]

    class Config:
        orm_mode = True


