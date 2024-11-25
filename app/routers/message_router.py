from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from HKS.data.database import get_db
from HKS.data.models import User
from HKS.data.queries import user_exists
from app.common import auth
from app.services.message_service import create_message, get_all_conversations, update_message

app = FastAPI()

messages_router = APIRouter(prefix='/api/messages', tags=['Messages'])


@messages_router.post("/{receiver_id}", status_code=201)
def send_message(
        receiver_id: str,
        text: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    if not user_exists(id=receiver_id, db=db):
        raise HTTPException(status_code=404, detail='Receiver does not exist')

    if not text:
        raise HTTPException(status_code=400, detail='Message cannot be empty')

    try:
        message = create_message(
            db=db,
            message_text=text,
            sender_id=current_user.id,
            receiver_id=receiver_id,
        )

        receiver = db.query(User).filter(User.id == receiver_id).first()
        return f'Message sent to {receiver.username}'
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error saving the message")


@messages_router.get("/conversation")
def get_conversation_(
        receiver_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    if not user_exists(id=receiver_id, db=db):
        raise HTTPException(status_code=404, detail='Receiver does not exist')

    messages = get_conversation(db=db, sender_id=current_user.id, receiver_id=receiver_id, current_user=current_user)

    return messages


@messages_router.get("/conversations")
def get_all_conversations_(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    conversation = get_all_conversations(db=db, current_user=current_user)
    return conversation or 'No messages found'


# RABOTI, NO TRQBVA DA SE DOBAVI HTTPEXCEPTION ZASHTOTO HVURLQ 500 PRI GRESHEN ID
@messages_router.patch("/{message_id}", status_code=201)
def update_message_(
        message_id: str,
        new_text: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    new_message = update_message(message_id=message_id, new_text=new_text, current_user=current_user, db=db)

    return new_message