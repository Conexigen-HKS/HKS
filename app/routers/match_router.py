"""
Match Router
In this file, we define the routes for the match service. We have two endpoints:
- get_matches: This endpoint is used to get all matches.
- send_match: This endpoint is used to send a match request.
"""
from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

from app.common import auth
from app.data.database import get_db
from app.data.models import User
from app.services.match_service import send_match_request, view_matches


app = FastAPI()

match_router = APIRouter(prefix='/api/matches', tags=['Matches'])


@match_router.get('/')
def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """
    Get all matches
    Accepts a database session and a current user object and returns a list of matches.
    """
    return view_matches(db=db, current_user=current_user)

@match_router.post('/match_request')
def send_match(
    target_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """
    Send a match request
    Accepts a target id, a database session, and a current user object and returns a match request.
    """
    return send_match_request(db=db, target_id=target_id, current_user=current_user)
