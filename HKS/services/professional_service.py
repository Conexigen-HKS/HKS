from sqlalchemy.orm import Session
from uuid import UUID
from HKS.data.schemas.professional import ProfessionalRegister, ProfessionalResponse
from app.data.models import Professional, User, ProfessionalProfile
from app.data.queries import search_job_ads



from sqlalchemy.orm import Session
from app.data.models import Professional, User
from app.data.schemas.professional import ProfessionalProfileCreate


def create_professional_profile(db: Session, user_id: UUID, profile_data: ProfessionalProfileCreate):
    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} does not exist")

    # Check if the user already has a professional profile
    if user.professional:
        raise ValueError(f"User with ID {user_id} already has a professional profile")

    # Create the professional profile
    new_profile = Professional(
        user_id=user_id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        address=profile_data.address,
        status=profile_data.status,
        summary=profile_data.summary,
        picture=profile_data.picture,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

#NOT TESTED:
def get_professional_by_id(db: Session, user_id: UUID) -> ProfessionalResponse:
    """
    Retrieve a professional profile by user ID.
    """
    professional = db.query(Professional).filter(Professional.user_id == user_id).first()
    if not professional:
        raise ValueError("Professional not found.")
    return ProfessionalResponse.model_validate(professional)


def get_profile_details(db: Session, professional_id: UUID):
    return db.query(ProfessionalProfile).filter_by(professional_id=professional_id).first()


def update_profile(db: Session, professional_id: UUID, update_data: dict):
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == professional_id).first()
    if not profile:
        raise ValueError("Profile not found")
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    return profile

def create_job_application(db: Session, professional_id: UUID, data: dict):
    application = ProfessionalProfile(**data, professional_id=professional_id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

def search_jobs(db: Session, filters: dict):
    return search_job_ads(db, filters)

def set_main_application(db: Session, professional_id: UUID, application_id: UUID):
    db.query(ProfessionalProfile).filter_by(professional_id=professional_id).update({"is_main_application": False})
    main_application = db.query(ProfessionalProfile).filter_by(id=application_id).first()
    if not main_application:
        raise ValueError("Application not found")
    main_application.is_main_application = True
    db.commit()
    return main_application


