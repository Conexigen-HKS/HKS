"""
Homepage service
In this file, we define the homepage service module.
This module contains helper functions for getting data for the homepage.
Functions:
- return_num_of_users: This function returns the number of users.
- num_of_successful_matches: This function returns the number of successful matches.
- get_active_job_ads_and_active_professionals:
This function returns the active job ads and active professionals.
"""

from sqlalchemy.orm import Session

from app.data.models import CompanyOffers, ProfessionalProfile, User, RequestsAndMatches


def return_num_of_users(db: Session) -> int:
    """
    Return the number of users
    :param db: The database session
    :return: The number of users
    """
    return db.query(User).count()


def num_of_successful_matches(db: Session) -> int:
    """
    Return the number of successful matches
    :param db: The database session
    :return: The number of successful matches
    """
    return db.query(RequestsAndMatches).filter(RequestsAndMatches.match).count()


def get_active_job_ads_and_active_professionals(db: Session) -> dict:  # FIXME
    """
    Get active job ads and active professionals
    :param db: The database session
    :return: A dictionary containing the active job ads and active professionals
    """
    active_job_ads = (
        db.query(CompanyOffers).filter(CompanyOffers.status == "active").all()
    )

    active_professionals_count = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.status == "active")
        .count()
    )

    return {
        "active_job_ads": active_job_ads,
        "active_professionals_count": active_professionals_count,
    }
