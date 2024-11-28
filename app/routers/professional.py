from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.data.database import get_db
from app.data.models import ProfessionalProfile, Professional, User
from app.data.schemas.professional import ProfessionalResponse, ProfessionalUpdate
from app.services.professional_service import update_professional_service, get_professional_service

app = FastAPI()

professional_router = APIRouter(prefix='/professional', tags=['Users'])

@professional_router.get("/", response_model=ProfessionalResponse)
def view_professional_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    professional = get_professional_service(db, current_user.id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return professional


@professional_router.put("/", response_model=ProfessionalResponse)
def update_professional_profile(
    update_data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_professional = update_professional_service(db, current_user.id, update_data)
    return updated_professional

@professional_router.patch("/matches")
def toggle_matches_visibility(is_visible: bool, db: Session = Depends(get_db), current_user: Professional = Depends(get_current_user)):
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.professional_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.requests_and_matches_visible = is_visible
    db.commit()
    return {"message": "Matches visibility updated", "is_visible": is_visible}


