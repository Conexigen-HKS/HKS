from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    username: str = Field(..., description="Username of the user", min_length=3, max_length=20)
    password: str = Field(..., description="Password of the user", min_length=6, max_length=20)

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, value: str):
        if (
            any(c.islower() for c in value) and
            any(c.isupper() for c in value) and
            any(c.isdigit() for c in value) and
            any(c in "%*@$!?" for c in value)
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )


class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str
    is_admin: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
