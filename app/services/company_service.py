import uuid
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy import func
from app.data.schemas.company import (CompanyInfoModel,
                                      CompanyAdModel, CompanyAdModel2, ShowCompanyModel)
<<<<<<< Updated upstream
from app.data.models import Companies, User, CompanyOffers
=======
from app.data.models import Companies, User, CompanyOffers, Location
>>>>>>> Stashed changes
from app.data.database import Session
import bcrypt


def show_company_description_service(user: User, db: Session):
    company = db.query(Companies).filter(Companies.user_id == user.id).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    company_ads = db.query(CompanyOffers).filter(CompanyOffers.status == "Active",
                                                 CompanyOffers.company_id == company.id).all()

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
            position_title=ad.title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location.city_name if ad.location else "N/A",
            status=ad.status
        ) for ad in company_ads],
    }


def edit_company_description_service(company_info: CompanyInfoModel, company_username: str):
    with Session() as s:
        user = s.query(User).filter(User.username == company_username).first()
        company = s.query(Companies).filter(Companies.user_id == user.id).first()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

<<<<<<< Updated upstream
        company_info_data = s.query(Companies).filter(Companies.id == company.id).first()
=======
        location = s.query(Location).filter(Location.city_name == company_info.company_location).first()
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Location '{company_info.company_location}' not found. Please provide a valid location."
            )

        company.description = company_info.company_description
        company.contacts = company_info.company_contacts
        company.picture = company_info.company_logo
        company.phone = company_info.phone
        company.email = company_info.email
        company.website = company_info.website
        company.location_id = location.id

        s.commit()

        company_ads_count = s.query(func.count(CompanyOffers.id)).filter(
            CompanyOffers.status == "Active", CompanyOffers.company_id == company.id
        ).scalar()
>>>>>>> Stashed changes

        if company_info_data is None:
            raise HTTPException(
                status_code=404,
                detail="Company information not found"
            )
        if company_info.company_description:
            company_info_data.description = company_info.company_description
        if company_info.company_contacts:
            company_info_data.contacts = company_info.company_contacts
        if company_info.company_logo:
            company_info_data.company_logo = company_info.company_logo

        # company_info_data.company_active_job_ads = company_info.company_active_job_ads
        if company_info.company_address:
            company_info_data.address = company_info.company_address
        s.commit()

        company_ads = s.query(CompanyOffers).filter(CompanyOffers.status == "Active").all()
        company_ads_by_len = s.query(func.count(CompanyOffers.id)).filter(CompanyOffers.status == "Active",
                                                                          CompanyOffers.company_id == company.id).scalar()
        return {
            "company_name": company.name,
<<<<<<< Updated upstream
            "company_description": company_info_data.description,
            "company_address": company_info_data.address,
            "company_contacts": company_info_data.contacts,
            "company_logo": company_info_data.company_logo,
            "company_active_job_ads": company_ads_by_len
        }


=======
            "company_description": company.description,
            "company_location": company_info.company_location,
            "company_contacts": company.contacts,
            "company_logo": company.picture,
            "company_active_job_ads": company_ads_count
        }



>>>>>>> Stashed changes
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




def find_all_companies_service():
    with Session() as session:
        companies = session.query(Companies).all()
        return [{attr: value for attr, value in company.__dict__.items() if attr != '_sa_instance_state'} for company in
                companies]
<<<<<<< Updated upstream
=======



>>>>>>> Stashed changes
