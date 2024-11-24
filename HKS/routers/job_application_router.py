from typing import List
from uuid import UUID
from venv import logger

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session

from HKS.common.auth import get_current_user
from HKS.services.job_application_service import get_professional_job_applications
from HKS.services.professional_service import create_company_offer, create_professional_application, \
    get_professional_profile_for_user

from app.data.database import get_db
from app.data.models import ProfessionalProfile, User, Professional, CompanyOffers
from app.data.schemas.job_application import CompanyOfferCreate,  CompanyOfferResponse, ProfessionalApplicationCreate

job_app_router = APIRouter(tags=["Job Applications"], prefix="/job_applications")



@job_app_router.post("/company-offers", response_model=CompanyOfferResponse)
def create_company_offer_endpoint(data: CompanyOfferCreate, db: Session = Depends(get_db)):

    offer = create_company_offer(
        db=db,
        company_id="company-id-placeholder",
        min_salary=data.min_salary,
        max_salary=data.max_salary,
        location=data.location,
        description=data.description,
        requirements=data.requirements
    )
    return offer

@job_app_router.post("/", response_model=CompanyOfferResponse)
def create_professional_application(data: ProfessionalApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    try:
        professional = db.query(Professional).filter(Professional.user_id == current_user.id).first()

        if not professional:
            logger.error("Professional not found for user_id: %s", current_user.id)
            raise HTTPException(status_code=404, detail="Professional not found.")

        professional_profile = db.query(ProfessionalProfile).filter(
            ProfessionalProfile.professional_id == professional.id
        ).first()

        if not professional_profile:
            logger.error("Professional profile not found for professional_id: %s", professional.id)
            raise HTTPException(status_code=404, detail="Professional profile not found.")

        application = CompanyOffers(
            professional_profile_id=professional_profile.id,
            type="professional",
            status="active",
            min_salary=data.min_salary,
            max_salary=data.max_salary,
            location=data.location,
            description=data.description
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        return CompanyOfferResponse(
            id=application.id,
            type=application.type,
            status=application.status,
            min_salary=application.min_salary,
            max_salary=application.max_salary,
            location=application.location,
            description=application.description,
            created_at=application.created_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")



# @job_app_router.put("/{application_id}", response_model=JobApplicationResponse)
# def update_application(application_id: str, update_data: JobApplicationUpdate, db: Session = Depends(get_db)):
#     application = update_job_application(db, application_id, update_data)
#     if not application:
#         raise HTTPException(status_code=404, detail="Job application not found")
#     return application
#
# @job_app_router.get("/search", response_model=List[JobApplicationResponse])
# def search_applications(min_salary: Optional[int] = None, location: Optional[str] = None, db: Session = Depends(get_db)):
#     return search_job_applications(db, min_salary, location)
#
# @job_app_router.post("/{application_id}/match", response_model=JobApplicationResponse)
# def match_application(application_id: str, professional_id: str, db: Session = Depends(get_db)):
#     application = match_job_application(db, application_id, professional_id)
#     if not application:
#         raise HTTPException(status_code=404, detail="Job application not found")
#     return application
#
#
# @job_app_router.post("/{professional_id}/upload-picture")
# def upload_profile_picture(professional_id: UUID, file: UploadFile, db: Session = Depends(get_db)):
#     if file.content_type not in ["image/jpeg", "image/png"]:
#         raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed.")
#     file_location = f"static/professional_pictures/{professional_id}_{file.filename}"
#     with open(file_location, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     profile = update_profile(db, professional_id, {"picture": file_location})
#     return {"message": "Profile picture uploaded successfully.", "profile": profile}
#

# @job_app_router.delete("/{application_id}")
# def delete_job_application(application_id: UUID, db: Session = Depends(get_db)):
#     delete_application(db, application_id)
#     return {"message": "Application deleted successfully"}
#
