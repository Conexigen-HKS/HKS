from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy import func
from app.data.schemas.company import (CompanyInfoModel,
                                      CompanyAdModel, CompanyAdModel2)
from app.data.models import Companies, User,CompanyOffers
from app.data.database import Session
import bcrypt


def edit_company_description_service(company_info: CompanyInfoModel, company_username: str):
    with Session() as s:
        company = s.query(Companies).filter(User.username == company_username).first()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        company_info_data = s.query(Companies).filter(Companies.id == company.id).first()
        company_active_job_ads = count_job_ads(company.id)
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

        company_info_data.company_active_job_ads = company_info.company_active_job_ads
        if company_info.company_address:
            company_info_data.address = company_info.company_address
        s.commit()

        return {
            "company_name": company.name,
            "company_description": company_info_data.description,
            "company_address": company_info_data.address,
            "company_contacts": company_info_data.contacts,
            "company_logo": company_info_data.company_logo,
            "company_active_job_ads": company_active_job_ads
        }


def count_job_ads(company_id):
    session = Session()
    count = session.query(func.count(CompanyOffers.id)).filter(CompanyOffers.company_id == company_id).scalar()
    session.close()

    return count


def create_new_ad_service(company_id: int, position_title: str,
                          min_salary: float, max_salary: float, job_description: str,
                          location: str, status) -> CompanyOffers:
    try:
        new_ad = CompanyOffers(
            company_id=company_id,
            position_title=position_title,
            min_salary=min_salary,
            max_salary=max_salary,
            job_description=job_description,
            location=location,
            status=status
        )

        with Session() as session:
            session.add(new_ad)
            session.commit()

        return new_ad
    except Exception as e:
        raise HTTPException(status_code=300, detail=str(e))

def get_company_id_by_user_id_service(user_id: str) -> int:
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


# def get_company_ads_service(username: str):
#     with Session() as session:
#         company_id = get_company_id_by_username_service(username)
#         ads = session.query(CompanyAdBase).filter(CompanyAdBase.company_id == company_id).all()
#         return [CompanyAdModel(**ad.__dict__) for ad in ads]
#
#
# def find_ad_by_id(ad_id: int, username: str):
#     with Session() as s:
#         ad = s.query(CompanyAdBase).filter(CompanyAdBase.company_ad_id == ad_id,
#                                            CompanyAdBase.company_id ==
#                                            get_company_id_by_username_service(username)).first()
#         return ad
#
#
# def edit_company_ad_by_id_service(ad_id: int, ad_info: CompanyAdModel2, username: str):
#     with Session() as s:
#         ad = s.query(CompanyAdBase) \
#             .filter(CompanyAdBase.company_ad_id == ad_id,
#                     CompanyAdBase.company_id == get_company_id_by_username_service(username)) \
#             .first()
#
#         if not ad:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Ad not found"
#             )
#         if ad_info.position_title:
#             ad.position_title = ad_info.position_title
#         if ad_info.salary:
#             ad.salary = ad_info.salary
#         if ad_info.job_description:
#             ad.job_description = ad_info.job_description
#         if ad_info.location:
#             ad.location = ad_info.location
#         if ad_info.ad_status is not None:
#             ad.ad_status = ad_info.ad_status
#
#         position_title = ad.position_title
#         salary = ad.salary
#         job_description = ad.job_description
#         location = ad.location
#         ad_status = ad.ad_status
#         s.commit()
#
#     return {
#         "position_title": position_title,
#         "salary": salary,
#         "job_description": job_description,
#         "location": location,
#         "ad_status": ad_status
#     }


def find_all_companies_service():
    with Session() as session:
        companies = session.query(Companies).all()
        return [{attr: value for attr, value in company.__dict__.items() if attr != '_sa_instance_state'} for company in
                companies]
