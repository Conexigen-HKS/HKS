import uuid
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.data.database import SessionLocal, Base, engine
from app.data.database_operations import create_user_if_not_exists, get_all_users, find_approved_professionals, \
    update_user_role, transaction_example, delete_user, count_professionals, get_messages_by_author, create_message
from app.data.models import User
from app.routers.employer import users_router

app = FastAPI()
app.include_router(users_router)
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



Base.metadata.create_all(bind=engine)

