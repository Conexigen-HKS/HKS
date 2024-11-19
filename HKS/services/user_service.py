import bcrypt
from sqlalchemy.orm import Session

from app.data.models import User
from app.data.queries import create_user, get_user_by_username


def register_user(username: str, password: str, role: str, db: Session):
    db_user = create_user(db, username, password, role=role)
    return {"username": db_user.username}

def authenticate_user(username: str, password: str, db: Session):
    user = get_user_by_username(db, username)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        return None
    return {"id": user.id, "username": user.username, "role": user.role}

def get_all_users(db: Session):
    """Retrieve all users from the database."""
    return db.query(User).all()