"""
Message service
In this file, we define the message service functions. We have four functions:
- exists: This function is used to check if a message exists.
- create_message: This function is used to create a new message.
- get_conversation: This function is used to get a conversation between two users.
- update_message: This function is used to update a message.
"""

from sqlalchemy import Boolean, and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.data.models import Message, User


def exists(db: Session, message_id: int) -> Boolean:
    """
    Check if a message exists in the database
    Parameters:
    message_id: int
    Returns:
    bool
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    return True if message else False


def create_message(
    db: Session, message_text: str, sender_id: str, receiver_id: str
) -> Message:
    """
    Create a new message in the database
    Parameters:
    message_text: str
    sender_id: int
    receiver_id: int
    """
    message = Message(
        content=message_text, author_id=sender_id, receiver_id=receiver_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation(db: Session, sender_id: str, receiver_id: str, current_user: User):
    """
    Get a conversation between two users
    Parameters:
    sender_id: int
    receiver_id: int
    current_user: User
    Returns:
    List[Message]
    """
    if current_user.is_admin:
        result = (
            db.query(Message)
            .filter(
                or_(
                    and_(
                        Message.author_id == sender_id,
                        Message.receiver_id == receiver_id,
                    ),
                    and_(
                        Message.author_id == receiver_id,
                        Message.receiver_id == sender_id,
                    ),
                )
            )
            .order_by(Message.created_at)
            .all()
        )
    else:
        result = (
            db.query(Message)
            .filter(
                or_(
                    and_(
                        Message.author_id == sender_id,
                        Message.receiver_id == receiver_id,
                    ),
                    and_(
                        Message.author_id == receiver_id,
                        Message.receiver_id == sender_id,
                    ),
                )
            )
            .order_by(Message.created_at)
            .all()
        )

        if not any(
            message.author_id == current_user.id
            or message.receiver_id == current_user.id
            for message in result
        ):
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this conversation.",
            )

    return result


def get_all_conversations(db: Session, current_user: User):
    """
    Get all conversations
    Parameters:
    current_user: User
    Returns:
    List[Message]
    """
    result = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.author_id == current_user.id),
                and_(Message.receiver_id == current_user.id),
            )
        )
        .order_by(Message.created_at)
        .all()
    )
    if not result:
        return []
    return result


def update_message(message_id: str, new_text: str, current_user: User, db: Session):
    """
    Update a message
    Parameters:
    message_id: int
    new_text: str
    current_user: User
    db: Session
    Returns:
    Message
    """
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to edit this message."
        )

    if new_text:
        message.content = new_text
        db.commit()
        db.refresh(message)
        return message
    else:
        raise HTTPException(
            status_code=403, detail="You are not authorized to view this conversation."
        )
