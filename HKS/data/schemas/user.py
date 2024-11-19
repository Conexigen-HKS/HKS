from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    password: str

    @classmethod
    def login_data(cls, username: str, password: str):
        return cls(username=username, password=password)

