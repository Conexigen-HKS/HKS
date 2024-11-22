from typing import Optional, List
from uuid import UUID

from pydantic import UUID4
from sqlalchemy.orm import Session

from HKS.data.schemas.job_application import  CompanyOfferCreate, \
    CompanyOfferResponse
from app.data.models import ProfessionalProfile, CompanyOffers
from app.data.queries import search_job_ads, create_company_offer


def create_offer_service(db: Session, offer_data: CompanyOfferCreate) -> CompanyOfferResponse:
    new_offer = CompanyOffers(
        company_id=offer_data.company_id,
        professional_profile_id=offer_data.professional_profile_id,
        type=offer_data.offer_type,
        status=offer_data.status,
        min_salary=offer_data.min_salary,
        max_salary=offer_data.max_salary,
        location=offer_data.location,
        description=offer_data.description,
    )
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return CompanyOfferResponse.from_orm(new_offer)

def get_professional_job_applications(db: Session, professional_profile_id: UUID):
    """Retrieve all job applications created by a professional."""
    return db.query(CompanyOffers).filter(
        CompanyOffers.professional_profile_id == professional_profile_id,
        CompanyOffers.type == "professional"
    ).all()
# def update_job_application(db: Session, application_id: UUID4, update_data: JobApplicationUpdate):
#     application = db.query(CompanyOffers).filter(CompanyOffers.id == application_id).first()
#     if not application:
#         return None
#     for key, value in update_data.dict(exclude_unset=True).items():
#         setattr(application, key, value)
#     db.commit()
#     db.refresh(application)
#     return application

def search_job_applications(db: Session, min_salary: Optional[int], location: Optional[str]):
    query = db.query(CompanyOffers).filter(CompanyOffers.status == "Active")
    if min_salary:
        query = query.filter(CompanyOffers.min_salary >= min_salary)
    if location:
        query = query.filter(CompanyOffers.location.ilike(f"%{location}%"))
    return query.all()

def match_job_application(db: Session, application_id: UUID4, professional_id: UUID4):
    application = db.query(CompanyOffers).filter(CompanyOffers.id == application_id).first()
    if not application:
        return None
    application.status = "Archived"
    application.chosen_professional_offer_id = professional_id
    db.commit()
    db.refresh(application)
    return application

def search_jobs(db: Session, filters: dict):
    return search_job_ads(db, filters)

def get_applications_by_status(db: Session, professional_id: UUID, status: Optional[str] = None):
    query = db.query(ProfessionalProfile).filter(ProfessionalProfile.professional_id == professional_id)
    if status:
        query = query.filter(ProfessionalProfile.status == status)
    return query.all()

def update_application(db: Session, application_id: UUID, update_data: dict):
    application = db.query(ProfessionalProfile).filter_by(id=application_id).first()
    if not application:
        raise ValueError("Application not found")
    for key, value in update_data.items():
        setattr(application, key, value)
    db.commit()
    return application

def delete_application(db: Session, application_id: UUID):
    application = db.query(ProfessionalProfile).filter_by(id=application_id).first()
    if not application:
        raise ValueError("Application not found")
    db.delete(application)
    db.commit()
