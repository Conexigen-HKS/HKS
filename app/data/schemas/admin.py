from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Admin(BaseModel):
    id: UUID | None = None
    username: str
    created_at: datetime

    @classmethod
    def from_query_results(cls, id, username, created_at):
        return cls(id = id,
                   username=username,
                   created_at = created_at)