from pydantic import BaseModel
from uuid import UUID

class LocationCreate(BaseModel):
    name: str

class LocationResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
