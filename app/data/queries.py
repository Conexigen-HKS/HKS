from sqlalchemy.orm import Session
import bcrypt

from app.data.models import User, Professional, ProfessionalProfile, Skills, Companies, Message


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()
def create_user(db: Session, username: str, password: str, role: str):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(username=username, hashed_password= hashed_password , role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# User Queries
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, role: str):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

# Professional Queries
def get_professional_by_user_id(db: Session, user_id: str):
    return db.query(Professional).filter(Professional.user_id == user_id).first()

def create_or_update_professional(db: Session, user_id: str, first_name: str, last_name: str, address: str, status: str):
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if professional:
        professional.first_name = first_name
        professional.last_name = last_name
        professional.address = address
        professional.status = status
    else:
        professional = Professional(user_id=user_id, first_name=first_name, last_name=last_name, address=address, status=status)
        db.add(professional)
    db.commit()
    db.refresh(professional)
    return professional

def get_approved_professionals(db: Session):
    return db.query(Professional).filter(Professional.is_approved.is_(True)).all()

# Professional Profile Queries
def get_professional_profile_by_id(db: Session, professional_id: str):
    return db.query(ProfessionalProfile).filter(ProfessionalProfile.professional_id == professional_id).first()

# Skill Queries
def get_skill_by_name(db: Session, skill_name: str):
    return db.query(Skills).filter(Skills.name == skill_name).first()

def create_skill(db: Session, skill_name: str):
    skill = Skills(name=skill_name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

# Company Queries
def get_company_by_user_id(db: Session, user_id: str):
    return db.query(Companies).filter(Companies.user_id == user_id).first()

# Message Queries
def create_message(db: Session, content: str, author_id: str, receiver_id: str):
    message = Message(content=content, author_id=author_id, receiver_id=receiver_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_by_user(db: Session, user_id: str):
    sent = db.query(Message).filter(Message.author_id == user_id).all()
    received = db.query(Message).filter(Message.receiver_id == user_id).all()
    return {"sent": sent, "received": received}
