import uuid
from sqlalchemy.orm import Session



# --- CREATE FUNCTIONS ---
def create_user_if_not_exists(db: Session, username: str, hashed_password: str, role: str = "professional", is_admin: bool = False):

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"User with username '{username}' already exists.")
        return existing_user
    else:
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            role=role,
            is_admin=is_admin
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def create_message(db: Session, content: str, author_id: uuid.UUID, receiver_id: uuid.UUID):

    new_message = Message(
        id=uuid.uuid4(),
        content=content,
        author_id=author_id,
        receiver_id=receiver_id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# --- READ FUNCTIONS ---

def get_all_users(db: Session):

    return db.query(User).all()


def get_user_by_id(db: Session, user_id: uuid.UUID):

    return db.query(User).filter(User.id == user_id).first()


def get_professional_profiles_above_min_salary(db: Session, min_salary: int):

    return db.query(ProfessionalProfile).filter(ProfessionalProfile.min_salary > min_salary).all()


def get_messages_by_author(db: Session, author_id: uuid.UUID):

    return db.query(Message).filter(Message.author_id == author_id).all()


# --- UPDATE FUNCTIONS ---

def update_user_role(db: Session, user_id: uuid.UUID, new_role: str):

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
    return None


# --- DELETE FUNCTIONS ---

from sqlalchemy.orm import Session
from app.data.models import User, Message, ProfessionalProfile, Professional


def delete_user(db: Session, user_id: uuid.UUID):

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.query(Message).filter((Message.author_id == user_id) | (Message.receiver_id == user_id)).delete(
            synchronize_session=False)

        db.delete(user)
        db.commit()
        return True
    return False


# --- ADVANCED QUERIES ---

def count_professionals(db: Session):

    return db.query(Professional).count()


def get_received_messages(db: Session, user_id: uuid.UUID):

    user = db.query(User).filter(User.id == user_id).first()
    return user.receiver_messages if user else []



def find_approved_professionals(db: Session):

    return db.query(Professional).join(User).filter(
        User.is_admin == False,
        User.role == "professional",
        Professional.is_approved == True
    ).all()


# --- TRANSACTION EXAMPLE ---

def transaction_example(db: Session, author_id: uuid.UUID, receiver_id: uuid.UUID, content: str):

    try:
        new_message = Message(
            id=uuid.uuid4(),
            content=content,
            author_id=author_id,
            receiver_id=receiver_id
        )
        db.add(new_message)

        receiver = db.query(User).filter(User.id == receiver_id).first()
        if receiver:
            receiver.role = "updated_role"

        db.commit()
        return new_message

    except Exception as e:
        db.rollback()
        print("Transaction failed:", e)
        return None
