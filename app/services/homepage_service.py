# DONE: Number of registered	employers and professionals 
# DONE: Number of successful matches 
# DONE: Current active job ads and applications 
from sqlalchemy.orm import Session
from app.data.models import CompanyOffers, ProfessionalProfile, User, RequestsAndMatches


def return_num_of_users(db: Session) -> int:
    return db.query(User).count()

def num_of_successful_matches(db: Session) -> int:
    return db.query(RequestsAndMatches).filter(RequestsAndMatches.match).count()

def get_active_job_ads_and_active_professionals(db: Session) -> dict: # TO FIX
    active_job_ads = db.query(CompanyOffers).filter(CompanyOffers.status == 'active').all()

    active_professionals_count = db.query(ProfessionalProfile).filter(ProfessionalProfile.status == 'active').count()

    return {
        "active_job_ads": active_job_ads,
        "active_professionals_count": active_professionals_count
    }


