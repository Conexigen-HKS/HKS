from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header, Query
from sqlalchemy.orm import Session
from app.common.responses import Forbidden
from app.data.models import User
from app.data.database import get_db
from app.common import auth
from app.services.admin_service import waiting_approvals, approve_user, delete_user
from app.data.schemas.admin import Admin

app = FastAPI()
#DA SI OPRAVQ RUTERITE, ZASHTOTO NE SPAZVAT RESTFUL !
admin_router = APIRouter(prefix='/api/admins', tags=['Admins'])

@admin_router.get("/")
def get_waiting_approvals(db: Session = Depends(get_db)):
    waiting_appr = waiting_approvals(db)

    return waiting_appr

@admin_router.patch("/{id}")
def approve_user_(
    id: str,
    role: Literal['professional', 'company'] = Query(...),
    db: Session = Depends(get_db)
    ):
    try:
        user_to_be_approved = approve_user(id=id, entity_type=role, db=db)
        return {"message": f"{role.capitalize()} approved successfully", "data": user_to_be_approved}
    except HTTPException as e:
        raise e

@admin_router.delete("/{user_id}")
async def delete_user_(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_admin_user)
):
    try:
        result = delete_user(id=id, db=db)
        return result
    except HTTPException as e:
        raise e
