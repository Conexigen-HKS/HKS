# services.py
from sqlalchemy.orm import Session
from app.data.models import User, Message, ProfessionalProfile

# --- User Services ---

def create_user(db: Session, username: str, hashed_password: str, role: str = "professional", is_admin: bool = False):
    new_user = User(username=username, hashed_password=hashed_password, role=role, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

# --- Message Services ---

def create_message(db: Session, content: str, author_id: str, receiver_id: str):
    new_message = Message(content=content, author_id=author_id, receiver_id=receiver_id)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages_by_user(db: Session, user_id: str):
    return db.query(Message).filter(Message.author_id == user_id).all()

# --- Professional Profile Services ---

def create_professional_profile(db: Session, user_id: str, description: str, min_salary: int, max_salary: int, status: str):
    new_profile = ProfessionalProfile(user_id=user_id, description=description, min_salary=min_salary, max_salary=max_salary, status=status)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

def get_professional_profile(db: Session, profile_id: str):
    return db.query(ProfessionalProfile).filter(ProfessionalProfile.id == profile_id).first()
