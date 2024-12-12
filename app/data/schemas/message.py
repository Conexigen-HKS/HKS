from uuid import UUID
from typing import Optional
from pydantic import BaseModel, model_validator


class Message(BaseModel):
    id: UUID | None = None
    sender_username: str | None = None
    receiver_username: str | None = None
    content: str

    @classmethod
    def from_query_result(cls, id, sender_username, receiver_username, content):
        return cls(
            id=id,
            sender_username=sender_username,
            receiver_username=receiver_username,
            content=content
        )

class SendMessageRequest(BaseModel):
    recipient_username: Optional[str] = None
    recipient_id: Optional[UUID] = None
    message_text: str

    @model_validator(mode="before")
    def validate_recipient(cls, values):
        if not values.get('recipient_username') and not values.get('recipient_id'):
            raise ValueError('Either recipient_username or recipient_id must be provided')
        return values