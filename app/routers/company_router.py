from typing import List, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header, Query
from sqlalchemy.orm import Session
from data.schemas.company import ShowCompanyModel
from data.models import User, Companies, CompanyOffers
from data.database import get_db
from common import auth
from services.company_service import show_company_description

app = FastAPI()

company_router = APIRouter(prefix="/companies", tags=["Companies"])

@company_router.get("/info", response_model=List[ShowCompanyModel])
def show_company_description_(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
    ):

    show_company = show_company_description(user=current_user,db=db)

    if show_company:
        return [show_company]
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while #fixthis company description"
        )