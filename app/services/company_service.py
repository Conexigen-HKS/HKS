"""
Company Service
In this file, we define the service functions that are used by the company controller.
These functions interact with the database to perform CRUD operations on the company model.
Functions:
- show_company_description_service: This function retrieves the company description.
- edit_company_description_service: This function edits the company description.
- count_job_ads: This function counts the number of job ads for a company.
- get_company_id_by_user_id_service: This function retrieves the company ID by user ID.
- get_company_name_by_username_service: This function retrieves the company name by username.
- find_all_companies_service: This function retrieves all companies.
- get_all_professionals: This function retrieves all professionals.
"""

from uuid import UUID
from typing import List, Literal

from fastapi import HTTPException
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from app.data.models import Companies, CompanyOffers, Location, Professional, User
from app.data.schemas.company import (
    CompanyAdModel,
    CompanyInfoRequestModel,
    SearchCompaniesModel,
)
from app.data.schemas.professional import ReturnProfessional

# TODO - View Archived Job Applications (Must Have):
# Missing Functionality: Companies should be able to view all archived (matched) job applications.
# Recommended Action: Implement functionality to list archived job applications for companies.

# TODO - Currently Active Number of Job Ads and Successful Matches:
# Missing Functionality: Display the number of active job ads and successful matches in the company info.

# TODO - Salary search range (must)
# Match threshold – percent of adds range increase (should)
# List of Skills/Requirements (must)
# Match threshold – number of skills that may miss from the add (should)
# Location (must)


def show_company_description_service(
    user: User, db: Session
):  # NOTE DA MAHNEM OBQVITE ZA RABOTA OT DESCRIPTION?
    """
    Show company description service
    This function retrieves the company description.
    :param user: The user object
    :param db: The database session
    :return: The company description
    """
    company = db.query(Companies).filter(Companies.user_id == user.id).first()

    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    company_ads = (
        db.query(CompanyOffers)
        .filter(
            func.lower(CompanyOffers.status) == "active".lower(),
            CompanyOffers.company_id == company.id,
        )
        .all()
    )

    return {
        "company_name": company.name,
        "company_description": company.description,
        "company_location": company.location.city_name if company.location else "N/A",
        "company_contacts": company.contacts,
        "company_phone": company.phone,
        "company_email": company.email,
        "company_website": company.website,
        "company_logo": company.picture,
        "company_active_job_ads": [
            CompanyAdModel(
                company_name=company.name,
                company_ad_id=str(ad.id),
                title=ad.title,
                min_salary=ad.min_salary,
                max_salary=ad.max_salary,
                description=ad.description,
                location=ad.location.city_name if ad.location else "N/A",
                status=ad.status,
            )
            for ad in company_ads
        ],
    }


def edit_company_description_service(
    company_info: CompanyInfoRequestModel, company_username: str, db: Session
):
    """
    Edit company description service
    This function edits the company description.
    :param company_info: The company info request model
    :param company_username: The company username
    :param db: The database session
    :return: The updated company info
    """
    user = db.query(User).filter(User.username == company_username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    company = db.query(Companies).filter(Companies.user_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company_info.company_location:
        location = (
            db.query(Location)
            .filter(Location.city_name == company_info.company_location)
            .first()
        )
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Location '{company_info.company_location}' not found. Please provide a valid location.",
            )
        company.location_id = location.id

    if company_info.company_description is not None:
        company.description = company_info.company_description
    if company_info.company_contacts is not None:
        company.contacts = company_info.company_contacts
    if company_info.company_logo is not None:
        company.picture = company_info.company_logo
    if company_info.phone is not None:
        company.phone = company_info.phone
    if company_info.email is not None:
        company.email = company_info.email
    if company_info.website is not None:
        company.website = company_info.website

    db.commit()

    return {
        "company_name": company.name,
        "company_description": company.description,
        "company_location": company.location.city_name if company.location else "N/A",
        "company_contacts": company.contacts,
        "company_logo": company.picture,
        "phone": company.phone,
        "email": company.email,
        "website": company.website,
    }


def count_job_ads(company_id: UUID, status: Literal['active', 'hidden', 'archived'], db: Session) -> int:
    """
    Count job ads
    This function counts the number of job ads for a company.
    :param company_id: The company ID
    :param status: The status of the job ad
    :param db: The database session
    :return: The number of job ads
    """
    try:
        count = (
            db.query(func.count(CompanyOffers.id))
            .filter(CompanyOffers.company_id == company_id, CompanyOffers.status == status)
            .scalar()
        )
    except HTTPException as e:
        db.rollback()
        raise HTTPException(f"Error counting job ads: {str(e)}") from e

    return count if count is not None else 0


def get_company_id_by_user_id_service(user_id: UUID) -> UUID:
    """
    Get company ID by user ID service
    This function retrieves the company ID by user ID.
    :param user_id: The user ID
    :return: The company ID
    """
    with Session() as session:
        try:
            company = (
                session.query(Companies).filter(Companies.user_id == user_id).one()
            )
            return company.id
        except Exception as exc:
            raise HTTPException(status_code=404, detail="Company not found") from exc


def get_company_name_by_username_service(company_id) -> str:
    """
    Get company name by username service
    This function retrieves the company name by username.
    :param company_id: The company ID
    :return: The company name
    """
    with Session() as session:
        try:
            company = session.query(Companies).filter(Companies.id == company_id).one()
            return company.name
        except Exception as exc:
            raise HTTPException(status_code=404, detail="Company not found") from exc


def find_all_companies_service(db: Session) -> List[CompanyInfoRequestModel]:
    """
    Find all companies service
    This function retrieves all companies.
    :param db: The database session
    :return: The list of companies
    """
    companies = db.query(Companies).all()

    result = []
    for company in companies:
        result.append(
            SearchCompaniesModel(
                company_name=company.name,
                company_description=company.description,
                company_location=company.location.city_name
                if company.location
                else "N/A",
                phone=company.phone,
                email=company.email,
                website=company.website,
                company_logo=company.picture,
            ).model_dump()
        )
    return result


def get_all_professionals(db: Session) -> List[ReturnProfessional]:
    """
    Get all professionals
    This function retrieves all professionals.
    :param db: The database session
    :return: The list of professionals
    """
    professionals = db.query(Professional).all()

    result = []
    for prof in professionals:
        result.append(
            ReturnProfessional(
                id=prof.id,
                first_name=prof.first_name,
                last_name=prof.last_name,
                location=prof.location.city_name if prof.location else "N/A",
                phone=prof.phone,
                email=prof.email,
                website=prof.website,
                summary=prof.summary,
                picture=prof.picture,
            ).model_dump()
        )
    return result
