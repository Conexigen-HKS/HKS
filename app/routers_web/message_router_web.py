from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
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
    # Subquery to get the latest message for each conversation
    subquery = (
        db.query(
            func.least(Message.author_id, Message.receiver_id).label("user1"),
            func.greatest(Message.author_id, Message.receiver_id).label("user2"),
            func.max(Message.created_at).label("latest_time")
        )
        .filter(
            (Message.author_id == current_user.id) | (Message.receiver_id == current_user.id)
        )
        .group_by("user1", "user2")
        .subquery()
    )

    # Join with messages to get the latest messages
    latest_messages = (
        db.query(Message)
        .join(
            subquery,
            (func.least(Message.author_id, Message.receiver_id) == subquery.c.user1) &
            (func.greatest(Message.author_id, Message.receiver_id) == subquery.c.user2) &
            (Message.created_at == subquery.c.latest_time)
        )
        .order_by(subquery.c.latest_time.desc())
        .all()
    )

    # Prepare data for the template
    conversations = []
    for message in latest_messages:
        other_user = message.receiver if message.author_id == current_user.id else message.author
        conversations.append({
            "user_id": str(other_user.id),
            "username": other_user.username,
            "content": message.content,
            "message_id": str(message.id),
            "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "conversations": conversations,
            "current_user_id": str(current_user.id),
        }
    )

@message_router_web.get("/messages/conversation/{other_user_id}")
async def get_conversation_with_user(
    other_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.author_id == current_user.id) & (Message.receiver_id == other_user_id)) |
        ((Message.author_id == other_user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()

    conversation = []
    for msg in messages:
        conversation.append({
            "sender_id": str(msg.author_id),
            "receiver_id": str(msg.receiver_id),
            "content": msg.content,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return conversation


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
    return {"detail": "Message sent successfully", "message_id": str(message.id)}

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


@message_router_web.get("/messages/conversation/{conversation_id}")
async def get_all_messages_in_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all messages between the two users
    messages = db.query(Message).filter(
        ((Message.author_id == current_user.id) & (Message.receiver_id == conversation_id)) |
        ((Message.receiver_id == current_user.id) & (Message.author_id == conversation_id))
    ).order_by(Message.created_at).all()

    return [
        {
            "sender": {"username": message.author.username},
            "receiver": {"username": message.receiver.username},
            "content": message.content,
            "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for message in messages
    ]
