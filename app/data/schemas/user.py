from pydantic import BaseModel
from typing import Optional, List


class UserRegistrationRequest(BaseModel):
    username: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: Optional[str] = None

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    user_id: str
    username: str
    user_role: Optional[str]
class UsersListResponse(BaseModel):
    users: List[UserResponse]