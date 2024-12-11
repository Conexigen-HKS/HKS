from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from app.common.auth import get_current_user
from app.data.models import Message, User
from app.data.schemas.message import SendMessageRequest
from app.services.message_service import (
    create_message,
    get_conversation,
    update_message,
    service_get_conversation_details
)
from app.data.database import get_db  # Import your database session dependency

message_router_web = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@message_router_web.get("/messages")
async def get_messages_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all conversations for the current user
    conversations = db.query(Message).filter(
        (Message.author_id == current_user.id) | 
        (Message.receiver_id == current_user.id)
    ).all()
    
    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "conversations": conversations
        }
    )


# Create a new message
@message_router_web.post("/messages/send")
def send_new_message(
    payload: SendMessageRequest,  # Accept the Pydantic model
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipient = db.query(User).filter(User.username == payload.recipient_username).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    message = create_message(db, payload.message_text, current_user.id, recipient.id)
    return {"detail": "Message sent successfully", "message_id": message.id}

@message_router_web.get("/messages/conversation-details/{conversation_id}")
async def get_conversation_details_endpoint(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = service_get_conversation_details(db, conversation_id, current_user)
    return {
        "sender": {"username": conversation.author.username},
        "receiver": {"username": conversation.receiver.username},
        "time": conversation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "content": conversation.content
    }


# Get a conversation between two users
@message_router_web.get("/messages/{sender_id}/{receiver_id}")
def get_conversation_between_users(
    sender_id: str,
    receiver_id: str,
    current_user: User = Depends(get_current_user),  # Assume you have a current user dependency
    db: Session = Depends(get_db)
):
    # Get conversation
    conversation = get_conversation(db, sender_id, receiver_id, current_user)
    return conversation


# Update a message
@message_router_web.put("/messages/{message_id}")
def update_existing_message(
    message_id: str, 
    new_text: str, 
    current_user: User = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    updated_message = update_message(message_id, new_text, current_user, db)
    return updated_message