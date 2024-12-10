"""
Message router
In this file, we define the routes for the message service. We have four endpoints:
- send_message: This endpoint is used to send a message.
- get_conversation: This endpoint is used to get a conversation between two users.
- get_all_conversations: This endpoint is used to get all conversations for a user.
- update_message: This endpoint is used to update a message.
"""

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.common import auth
from app.data.database import get_db
from app.data.models import User
from app.services.message_service import (
    create_message,
    get_all_conversations,
    get_conversation,
    update_message,
)
from app.services.user_services import user_exists


app = FastAPI()

messages_router = APIRouter(prefix="/api/messages", tags=["Messages"])


@messages_router.post("/{receiver_id}", status_code=201)
def send_message(
    receiver_id: str,
    text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Send a message
    Accepts a receiver id, a message text, a database session, and a current user object.
    Returns a message.
    """
    if not user_exists(id=receiver_id, db=db):
        raise HTTPException(status_code=404, detail="Receiver does not exist")

    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        message = create_message(
            db=db,
            message_text=text,
            sender_id=current_user.id,
            receiver_id=receiver_id,
        )

        receiver = db.query(User).filter(User.id == receiver_id).first()
        return f"Message sent to {receiver.username}"
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error saving the message") from exc


@messages_router.get("/conversation")
def get_conversation_(
    receiver_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Get a conversation
    Accepts a receiver id, a database session, and a current user object.
    Returns a conversation between the current user and the receiver.
    """
    if not user_exists(id=receiver_id, db=db):
        raise HTTPException(status_code=404, detail="Receiver does not exist")

    messages = get_conversation(
        db=db,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        current_user=current_user,
    )

    return messages


@messages_router.get("/conversations")
def get_all_conversations_(
    db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
    """
    Get all conversations
    Accepts a database session and a current user object.
    Returns all conversations for the current user.
    """
    conversation = get_all_conversations(db=db, current_user=current_user)
    return conversation or "No messages found"


# FIXME RABOTI, NO TRQBVA DA SE DOBAVI HTTPEXCEPTION ZASHTOTO HVURLQ 500 PRI GRESHEN ID
@messages_router.patch("/{message_id}", status_code=201)
def update_message_(
    message_id: str,
    new_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Update a message
    Accepts a message id, a new message text, a database session, and a current user object.
    Returns the updated message.
    """
    new_message = update_message(
        message_id=message_id, new_text=new_text, current_user=current_user, db=db
    )

    return new_message
