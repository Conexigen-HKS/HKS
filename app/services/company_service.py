from typing import List
import uuid
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.data.schemas.company import (
    CompanyAdModel,
    CompanyInfoRequestModel,
    SearchCompaniesModel
)
from app.data.models import Companies, Professional, User, CompanyOffers, Location
from app.data.schemas.professional import ProfessionalOut, ReturnProfessional
 
 
# TODO Professionals Search for Companies and Vice Versa (Should Have):
# TODO View Archived Job Applications (Must Have):
# Missing Functionality: Companies should be able to view all archived (matched) job applications.
# Recommended Action: Implement functionality to list archived job applications for companies.
# TODO Currently Active Number of Job Ads and Successful Matches:
# Missing Functionality: Display the number of active job ads and successful matches in the company info.
# TODO Salary search range (must)
# Match threshold – percent of adds range increase (should)
# List of Skills/Requirements (must)
# Match threshold – number of skills that may miss from the add (should)
# Location (must)
 
# WORKS
def show_company_description_service(user: User, db: Session):  # DA MAHNEM OBQVITE ZA RABOTA OT DESCRIPTION
    company = db.query(Companies).filter(Companies.user_id == user.id).first()
 
    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
 
    company_ads = db.query(CompanyOffers).filter(
        func.lower(CompanyOffers.status) == "active".lower(),
        CompanyOffers.company_id == company.id
    ).all()
 
    return {
        "company_name": company.name,
        "company_description": company.description,
        "company_location": company.location.city_name if company.location else "N/A",
        "company_contacts": company.contacts,
        "company_phone": company.phone,
        "company_email": company.email,
        "company_website": company.website,
        "company_logo": company.picture,
        "company_active_job_ads": [CompanyAdModel(
            company_name=company.name,
            company_ad_id=str(ad.id),
            title=ad.title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location.city_name if ad.location else "N/A",
            status=ad.status
        ) for ad in company_ads],
    }
 
 
# WORKS
def edit_company_description_service(company_info: CompanyInfoRequestModel, company_username: str, db: Session):
    user = db.query(User).filter(User.username == company_username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found.'
        )
 
    company = db.query(Companies).filter(Companies.user_id == user.id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
 
    if company_info.company_location:
        location = db.query(Location).filter(
            Location.city_name == company_info.company_location
        ).first()
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Location '{company_info.company_location}' not found. Please provide a valid location."
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
        "website": company.website
    }
 
 
def count_job_ads(company_id):
    session = Session()
    count = session.query(func.count(CompanyOffers.id)).filter(CompanyOffers.company_id == company_id).scalar()
    session.close()
 
    return count
 
 
def get_company_id_by_user_id_service(user_id: uuid) -> uuid:
    with Session() as session:
        try:
            company = session.query(Companies).filter(Companies.user_id == user_id).one()
            return company.id
        except:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
 
 
def get_company_name_by_username_service(company_id) -> str:
    with Session() as session:
        try:
            company = session.query(Companies).filter(Companies.id == company_id).one()
            return company.name
        except:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
 
 
# def find_ad_by_id(ad_id: int, username: str):
#     with Session() as s:
#         ad = s.query(CompanyAdBase).filter(CompanyAdBase.company_ad_id == ad_id,
#                                            CompanyAdBase.company_id ==
#                                            get_company_id_by_username_service(username)).first()
#         return ad
 
 
# WORKS
def find_all_companies_service(db: Session) -> List[CompanyInfoRequestModel]:
    companies = db.query(Companies).all()
 
    result = []
    for company in companies:
        result.append(SearchCompaniesModel(
            company_name=company.name,
            company_description=company.description,
            company_location=company.location.city_name if company.location else "N/A",
            phone=company.phone,
            email=company.email,
            website=company.website,
            company_logo=company.picture
        ).model_dump())
    return result
 
 
# WORKS
def get_all_professionals(db: Session) -> List[ReturnProfessional]:
    professionals = db.query(Professional).all()
 
    result = []
    for prof in professionals:
        result.append(ReturnProfessional(
            id=prof.id,
            first_name=prof.first_name,
            last_name=prof.last_name,
            location=prof.location.city_name if prof.location else "N/A",
            phone=prof.phone,
            email=prof.email,
            website=prof.website,
            summary=prof.summary,
            picture=prof.picture
        ).model_dump())
    return result
 