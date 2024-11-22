import shutil

from pydantic import ValidationError
from rest_framework import status

from HKS.data.schemas.job_application import CompanyOfferResponse, CompanyOfferCreate
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from HKS.services.job_application_service import (update_application, delete_application,
                                                  search_job_applications, match_job_application,
                                                  get_professional_job_applications,
                                                  create_offer_service)
from HKS.services.professional_service import create_job_application, search_jobs, update_profile
from app.data.database import get_db
from app.data.schemas.job_application import JobApplicationCreate, SearchJobAds

job_app_router = APIRouter(tags=["Job Applications"], prefix="/job_applications")


@job_app_router.post("/", response_model=CompanyOfferResponse, summary="Create a new offer or application")
def create_offer(offer_data: CompanyOfferCreate, db: Session = Depends(get_db)):
    """
    Create a new job offer (company) or job application (professional).
    """
    try:
        return create_offer_service(db, offer_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @job_app_router.get("/{professional_profile_id}", response_model=List[JobApplicationResponse])
# def get_professional_applications(
#     professional_profile_id: UUID,
#     db: Session = Depends(get_db),
# ):
#     """Retrieve job applications for a professional."""
#     applications = get_professional_job_applications(db, professional_profile_id)
#     return applications
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
#
# # @job_app_router.delete("/{application_id}")
# # def delete_job_application(application_id: UUID, db: Session = Depends(get_db)):
# #     delete_application(db, application_id)
# #     return {"message": "Application deleted successfully"}
# #
