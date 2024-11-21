from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class ProfessionalResponse(BaseModel):
    id: UUID #tova go nqmashe
    first_name: str
    last_name: str
    address: str
    status: Optional[str]
    summary: Optional[str]
    is_approved: bool
    # username: str
    user_id: UUID #promeneno na uuid ot str

    model_config = ConfigDict(from_attributes=True)

class ProfessionalOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    address: str
    is_approved: bool
    username: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ProfessionalRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    address: str
    summary: Optional[str] = None