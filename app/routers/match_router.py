from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from HKS.data.database import get_db
from HKS.data.models import User
from app.common import auth
from app.services.match_service import view_matches, send_match_request

app = FastAPI()

match_router = APIRouter(prefix='/api/matches', tags=['Matches'])

@match_router.get('/')
def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    return view_matches(db=db, current_user=current_user)

@match_router.post('/match_request')
def send_match(
    company_offer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    return send_match_request(db=db, offer_id=company_offer_id, current_user=current_user)