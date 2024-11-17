# main.py (or the entry point of your application)
import uuid
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.data.database import SessionLocal, Base, engine
from app.data.database_operations import create_user_if_not_exists, get_all_users, find_approved_professionals, \
    update_user_role, transaction_example, delete_user, count_professionals, get_messages_by_author, create_message
from app.data.models import User, Message
from app.routers.employer import users_router

app = FastAPI()
app.include_router(users_router)

try:
    with engine.connect() as connection:
        print("Connection to the database was successful.")
except Exception as e:
    print("Error connecting to the database:", e)
print("Tables created by SQLAlchemy:")
for table in Base.metadata.tables:
    print(table)