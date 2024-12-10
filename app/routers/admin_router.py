"""
This module contains the admin_router which contains the routes for the admin
It includes the following routes:
    - get_waiting_approvals
    - approve_user_
    - delete_user_
    - block_unblock_user
"""
# TODO Admins can delete application data (profiles, job ads etc.)
from typing import Literal, Union

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.data.models import Companies, Professional, User
from app.data.database import get_db
from app.common import auth
from app.data.schemas.company import CompanyOutput
from app.data.schemas.professional import ProfessionalOutput
from app.services.admin_service import (
    block_or_unblock_user,
    waiting_approvals,
    approve_user,
    delete_user,
)


app = FastAPI()
admin_router = APIRouter(prefix="/api/admins", tags=["Admins"])


@admin_router.get("/")
def get_waiting_approvals(
    db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)
):
    """
    Returns a list of users that are waiting for approval
    Method: GET
    Accepts: None
    Returns: List of users
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=401)

    waiting_appr = waiting_approvals(db)
    return waiting_appr


@admin_router.patch("/{id}")
def approve_user_(
    id: str,
    role: Literal["professional", "company"] = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Approves a user based on the user_id and role
    Method: PATCH
    Accepts: user_id, role
    Returns: JSONResponse or HTTPException depending on the outcome
    """

    if current_user.role != "admin":
        raise HTTPException(status_code=401)

    try:
        user_to_be_approved = approve_user(id=id, entity_type=role, db=db)
        return JSONResponse(
            status_code=200,
            content={
                "message": f"{role.capitalize()} approved successfully",
                "data": user_to_be_approved,
            },
        )
    except HTTPException as e:
        raise e


@admin_router.delete("/{user_id}")
def delete_user_(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Deletes a user based on the user_id
    Method: DELETE
    Accepts: user_id
    Returns: HTTPException
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=401)

    try:
        delete_user(id=id, db=db)
        return JSONResponse(
            status_code=200, content={"message": "User deleted successfully"}
        )

    except HTTPException as e:
        raise e


@admin_router.patch(
    "/block-unblock/{user_id}", response_model=Union[ProfessionalOutput, CompanyOutput]
)
def block_unblock_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    blocked_user = block_or_unblock_user(user_id, db, current_user)

    if isinstance(blocked_user, Professional):
        return ProfessionalOutput.model_validate(blocked_user)
    elif isinstance(blocked_user, Companies):
        return CompanyOutput.model_validate(blocked_user)
    else:
        raise HTTPException(status_code=500, detail="Unexpected user type returned")
