from pydantic import BaseModel
from uuid import UUID

class Admin(BaseModel):
    id: UUID | None = None
    username: str

    @classmethod
    def from_query_results(cls, id, username):
        return cls(id = id,
                   username=username)