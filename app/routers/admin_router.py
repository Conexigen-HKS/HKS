from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header, Query
from sqlalchemy.orm import Session
from common.responses import Forbidden
from data.models import User
from data.database import get_db
from common import auth
from services.admin_service import waiting_approvals, approve_user, delete_user
from data.schemas.admin import Admin

app = FastAPI()

admin_router = APIRouter(prefix='/api/admins', tags=['Admins'])

@admin_router.get("/")
def get_waiting_approvals(db: Session = Depends(get_db)):
    waiting_appr = waiting_approvals(db)

    return waiting_appr

@admin_router.patch("/approve/{id}")
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

#НЕ РАБОТИ - ТРЯБВА ДА СЕ СЛОЖИ ONDELETE - CASCADE
@admin_router.delete("/{id}")
def delete_user_(
    id: str,
    db: Session = Depends(get_db)
    ):
    user_to_be_del = delete_user(id=id, db=db)
    return user_to_be_del
