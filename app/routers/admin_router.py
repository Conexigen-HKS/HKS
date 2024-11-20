from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session
from app.common.responses import Forbidden
from app.data.models import User
from data.database import get_db
from common import auth
from services.admin_service import get_admin_by_id, approve_proffesional, approve_company, waiting_approvals
from data.schemas.admin import Admin

app = FastAPI()

admin_router = APIRouter(prefix='/api/admins', tags=['Admins'])

@admin_router.get("/admin/{id}", tags=["Admin"])
def get_admin_by_id_r(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth.get_current_admin_user)
):
    admin = get_admin_by_id(id, db)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")  # По-добър статус код

    return {
        "id": admin.id,
        "username": admin.username,
        "role": admin.role,
        "created_at": admin.created_at,
    }