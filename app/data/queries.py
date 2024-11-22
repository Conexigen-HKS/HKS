from http.client import HTTPException
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from HKS.common.utils import get_password_hash
from HKS.data.schemas.professional import ProfessionalResponse
from app.data.models import Companies, User, Professional, ProfessionalProfile, CompanyOffers, \
    CompaniesRequirements
from app.data.schemas.company import CompanyResponse, CompanyRegister

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




def get_professional_profile(db: Session, professional_id: UUID):
    return db.query(ProfessionalProfile).filter(ProfessionalProfile.professional_id == professional_id).first()


def update_professional_profile(db: Session, professional_id: UUID, data: dict):
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.professional_id == professional_id).first()
    if profile:
        for key, value in data.items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
    return profile


def get_all_applications(db: Session, professional_id: UUID):
    return db.query(ProfessionalProfile).filter(ProfessionalProfile.professional_id == professional_id).all()


def search_job_ads(db: Session, filters: dict):
    query = db.query(CompanyOffers)
    if filters.get("title"):
        query = query.filter(CompanyOffers.status.ilike(f"%{filters['title']}%"))
    if filters.get("location"):
        query = query.filter(CompanyOffers.location.ilike(f"%{filters['location']}%"))
    if filters.get("min_salary"):
        query = query.filter(CompanyOffers.min_salary >= filters["min_salary"])
    if filters.get("max_salary"):
        query = query.filter(CompanyOffers.max_salary <= filters["max_salary"])
    if filters.get("skills"):
        query = query.join(CompaniesRequirements).filter(CompaniesRequirements.title.in_(filters["skills"]))
    return query.all()

def create_company_offer(
    db: Session,
    company_id: UUID = None,
    professional_profile_id: UUID = None,
    offer_type: str = "company",
    status: str = "active",
    min_salary: int = 0,
    max_salary: int = 2147483647,
    location: str = None,
    description: str = None
) -> CompanyOffers:
    new_offer = CompanyOffers(
        company_id=company_id,
        professional_profile_id=professional_profile_id,
        type=offer_type,
        status=status,
        min_salary=min_salary,
        max_salary=max_salary,
        location=location,
        description=description
    )
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer