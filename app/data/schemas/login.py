from app.common.utils import ValidUsername, ValidPassword
from pydantic import BaseModel, field_validator

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