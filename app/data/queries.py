from http.client import HTTPException

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from HKS.common.utils import get_password_hash
from app.data.models import Companies, User, Professional
from app.data.schemas.company import CompanyResponse, CompanyRegister
from app.data.schemas.professional import ProfessionalResponse, ProfessionalRegister
from app.data.schemas.user import UserResponse


def get_user(db: Session, username: str) -> UserResponse:
    """
    Retrieve a user by username and return its response model.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_admin=user.is_admin
    )


def create_professional(db: Session, professional_data: ProfessionalRegister) -> ProfessionalResponse:
    """
    Create and return a new professional.
    """
    try:
        hashed_password = get_password_hash(professional_data.password)
        user = User(username=professional_data.username, hashed_password=hashed_password, role="professional")
        db.add(user)
        db.commit()
        db.refresh(user)

        professional = Professional(
            user_id=user.id,
            **professional_data.dict(exclude={"username", "password"})
        )
        db.add(professional)
        db.commit()
        db.refresh(professional)
        return ProfessionalResponse.model_validate(professional)
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error creating professional: {e}")


def create_company(db: Session, company_data: CompanyRegister) -> CompanyResponse:
    """
    Create and return a new company.
    """
    try:
        hashed_password = get_password_hash(company_data.password)
        user = User(username=company_data.username, hashed_password=hashed_password, role="company")
        db.add(user)
        db.commit()
        db.refresh(user)

        company = Companies(
            user_id=user.id,
            **company_data.dict(exclude={"username", "password"})
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return CompanyResponse.model_validate(company)
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error creating company: {e}")


def get_all_users(db: Session, role: str):
    """
    Retrieve all users of a specified role and return a list of response models.
    """
    if role == "professional":
        professionals = db.query(Professional).join(User).filter(User.role == "professional").all()
        return [ProfessionalResponse.model_validate(professional) for professional in professionals]
    elif role == "company":
        companies = db.query(Companies).join(User).filter(User.role == "company").all()
        return [CompanyResponse.model_validate(company) for company in companies]
    else:
        raise HTTPException(status_code=400, detail="Invalid role")