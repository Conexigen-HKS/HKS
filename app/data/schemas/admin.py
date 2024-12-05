from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Admin(BaseModel):
    id: UUID | None = None
    username: str
    created_at: datetime

    @classmethod
    def from_query_results(cls, id, username, created_at):
        """
        This method is used to create an instance of the Admin class from the results of a query.
        """
        return cls(id = id,
                   username=username,
                   created_at = created_at)