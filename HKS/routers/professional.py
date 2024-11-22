from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from HKS.services.job_application_service import get_applications_by_status
from HKS.services.professional_service import get_profile_details, update_profile, set_main_application, \
    create_professional_profile
from app.data.database import get_db
from app.data.schemas.professional import ProfessionalProfileResponse, ProfessionalProfileUpdate, \
    ProfessionalProfileCreate

professional_router = APIRouter(tags=["Professionals"], prefix="/professionals")

@professional_router.post("/{user_id}/create-profile", response_model=ProfessionalProfileResponse)
def create_profile(user_id: UUID, profile_data: ProfessionalProfileCreate, db: Session = Depends(get_db)):
    try:
        profile = create_professional_profile(db, user_id, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while creating the profile")



#NOT TESTED:
@professional_router.get("/{professional_id}", response_model=ProfessionalProfileResponse)
def get_profile(professional_id: UUID, db: Session = Depends(get_db)):
    return get_profile_details(db, professional_id)


@professional_router.put("/{professional_id}", response_model=ProfessionalProfileResponse)
def edit_profile(professional_id: UUID, data: ProfessionalProfileUpdate, db: Session = Depends(get_db)):
    return update_profile(db, professional_id, data.dict())

@professional_router.get("/{professional_id}/applications")
def get_professional_applications(professional_id: UUID, status: Optional[str] = None, db: Session = Depends(get_db)):
    return get_applications_by_status(db, professional_id, status)


@professional_router.post("/{professional_id}/set-main-application/{application_id}")
def set_main(professional_id: UUID, application_id: UUID, db: Session = Depends(get_db)):
    return set_main_application(db, professional_id, application_id)
