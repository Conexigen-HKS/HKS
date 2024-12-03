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
def get_waiting_approvals(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=401
        )
    
    waiting_appr = waiting_approvals(db)
    return waiting_appr

@admin_router.patch("/{id}")
def approve_user_(
    id: str,
    role: Literal['professional', 'company'] = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
    ):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=401
        )
    
    try:
        user_to_be_approved = approve_user(id=id, entity_type=role, db=db)
        return {"message": f"{role.capitalize()} approved successfully", "data": user_to_be_approved}
    except HTTPException as e:
        raise e

@admin_router.delete("/{user_id}")
def delete_user_(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=401
        )
    
    try:
       delete_user(id=id, db=db)
       return HTTPException(
           status_code=200,
           detail='User deleted successfully'
       )
    
    except HTTPException as e:
        raise e

# Administration (could)


# Optionally, create application administration functionality

# o Admins approve companies’ and professionals’ registration

# o Admins can block/unblock companies and professionals

# o Admins can delete application data (profiles, job ads etc.)

# o Admins can add/delete or approve skills/requirements