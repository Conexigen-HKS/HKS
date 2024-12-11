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
    subquery = (
        db.query(
        )
        .subquery()
    )

        db.query(Message)
        .join(
            subquery,
            (func.greatest(Message.author_id, Message.receiver_id) == subquery.c.user_pair)
            & (func.least(Message.author_id, Message.receiver_id) == subquery.c.pair_partner)
            & (Message.created_at == subquery.c.latest_time),
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "messages.html",
        {
            "request": request,
            "conversations": conversations,
            "current_user": current_user,
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


@message_router_web.get("/messages/conversation/{sender_id}/{receiver_id}")
def get_conversation_between_users(
    sender_id: str,
    receiver_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.author_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.author_id == receiver_id) & (Message.receiver_id == sender_id))
    ).order_by(Message.created_at).all()

    return {
        "messages": [
            {"sender": m.author.username, "content": m.content, "time": m.created_at.strftime("%Y-%m-%d %H:%M:%S")}
            for m in messages
        ]
    }


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

    if not messages:
        return []

    return [
        {
            "sender": {"id": message.author_id, "username": message.author.username},
            "receiver": {"id": message.receiver_id, "username": message.receiver.username},
            "content": message.content,
            "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for message in messages
    ]


# Get a conversation between two users
@message_router_web.get("/messages/{sender_id}/{receiver_id}")
def get_conversation_between_users(
    sender_id: str,
    receiver_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.author_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.author_id == receiver_id) & (Message.receiver_id == sender_id))
    ).order_by(Message.created_at).all()

    return {"messages": [{"sender": m.author.username, "content": m.content, "time": m.created_at} for m in messages]}


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