from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from HKS.common.utils import get_password_hash
from app.data.models import User, Professional, Companies
from app.data.queries import create_company_record, get_user_by_username, get_all_users_by_role, user_exists, \
    create_user
from app.data.schemas.user import UserResponse


def register_basic_user_service(db: Session, user_data: dict):
    existing_user = get_user_by_username(db, user_data["username"])
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    user_data["role"] = "basic"

    created_user = create_user(db, user_data)

    return {
        "id": created_user.id,
        "username": created_user.username,
        "role": created_user.role,
        "is_admin": created_user.is_admin or False,
        "created_at": created_user.created_at.isoformat() if created_user.created_at else None
    }


def get_user(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_professional(db: Session, username: str) -> Professional:
    professional = db.query(Professional).filter(Professional.username == username).first()

    if not professional:
        return None

    return professional


def return_professional_response():
    raise NotImplementedError


def create_company_service(db: Session, company_data, username: str):
    user = get_user_by_username(db, username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    hashed_password = get_password_hash(company_data.password)
    user = User(
        username=company_data.username,
        hashed_password=hashed_password,
        role="company"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    company_dict = {
        "name": company_data.company_name,
        "description": company_data.description,
        "address": company_data.address,
        "contacts": "",
        "is_approved": False,
    }
    return create_company_record(db, user.id, company_dict)


def get_company(db: Session, username: str) -> Companies:
    company = db.query(Companies).filter(Companies.username == username).first()

    if not company:
        return None

    return company




def get_user_by_id(db: Session, user_id: UUID) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role
    )

def get_all_users_service(db: Session, role: str):
    if role not in ['professional', 'company']:
        raise HTTPException(status_code=400, detail="Invalid role specified.")

    entities = get_all_users_by_role(db, role)
    if role == "professional":
        return [
            {
                "id": prof.id,
                "username": user.username,
                "first_name": prof.first_name,
                "last_name": prof.last_name,
                "address": prof.address,
                "summary": prof.summary,
                "status": prof.status,
                "is_approved": prof.is_approved,
            }
            for prof, user in entities
        ]
    elif role == "company":
        return [
            {
                "id": company.id,
                "username": user.username,
                "name": company.name,
                "description": company.description,
                "address": company.address,
                "contacts": company.contacts,
                "is_approved": company.is_approved,
            }
            for company, user in entities
        ]


def get_username_from_id(usr_id: str, db: Session):
    user = db.query(User).filter(User.id == usr_id).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {usr_id} not found !")
    return user.username


def user_exists_service(db: Session, user_id: UUID):
    return user_exists(db, user_id)
