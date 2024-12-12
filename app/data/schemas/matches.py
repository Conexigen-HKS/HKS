from pydantic import BaseModel
from typing import Optional

class MatchRequest(BaseModel):
    target_id: str
    action: str
    profile_or_offer_id: Optional[str] = None