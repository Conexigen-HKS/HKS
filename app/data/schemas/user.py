from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict

from HKS.common.utils import ValidUsername, ValidPassword


class Login(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def validate_username(cls, v):
        if not ValidUsername.match(v):
            raise ValueError('Invalid username format')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if not ValidPassword.match(v):
            raise ValueError('Invalid password format')
        return v

class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    is_admin: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
