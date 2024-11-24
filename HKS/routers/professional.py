import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from HKS.common.auth import get_current_user
from HKS.services.professional_service import upgrade_user_to_professional_service
from app.data.database import get_db
from app.data.models import User
from app.data.schemas.professional import ProfessionalUpgrade

professional_router = APIRouter(prefix="/professionals", tags=["Professionals"])


@professional_router.put("/upgrade")
def upgrade_to_professional(professional_data: ProfessionalUpgrade, current_user: tuple[User, dict] = Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_user
    user_id = user.id

    if user.role != "basic":
        raise HTTPException(status_code=400, detail="Only basic users can be upgraded to professional.")

    professional = upgrade_user_to_professional_service(db, user_id, professional_data)


    return professional

