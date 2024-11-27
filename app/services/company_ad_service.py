import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import func
from app.data.schemas.company import (CompanyInfoModel,
                                      CompanyAdModel, CompanyAdModel2, ShowCompanyModel)
from app.data.models import Companies, User, CompanyOffers
from app.data.database import Session
from app.services.company_service import get_company_id_by_user_id_service, get_company_name_by_username_service


def create_new_ad_service(company_id: str, position_title: str,
                          min_salary: float, max_salary: float, job_description: str,
                          location: str, status) -> CompanyOffers:
    try:
        new_ad = CompanyOffers(
            company_id=str(company_id),
            position_title=position_title,
            min_salary=min_salary,
            max_salary=max_salary,
            description=job_description,
            location=location,
            status=status
        )

        with Session() as session:
            session.add(new_ad)
            session.commit()

        return new_ad
    except Exception as e:
        raise HTTPException(status_code=300, detail=str(e))


def get_company_ads_service(user_id: uuid, company_name: str):
    with Session() as session:
        company_id = get_company_id_by_user_id_service(user_id)

        ads = session.query(CompanyOffers).filter(CompanyOffers.company_id == company_id).all()
        return [CompanyAdModel(
            company_name=company_name,
            company_ad_id=str(ad.id),
            position_title=ad.position_title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location,
            status=ad.status
        ) for ad in ads]

def edit_company_ad_by_position_title_service(position_title: str, ad_info: CompanyAdModel2, user_id: str):
    with Session() as s:
        ad = s.query(CompanyOffers) \
            .filter(CompanyOffers.id == position_title,
                    CompanyOffers.company_id == get_company_id_by_user_id_service(user_id)) \
            .first()

        if not ad:
            raise HTTPException(
                status_code=404,
                detail="Ad not found"
            )
        if ad_info.position_title:
            ad.position_title = ad_info.position_title
        if ad_info.min_salary:
            ad.min_salary = ad_info.min_salary
        if ad_info.max_salary:
            ad.max_salary = ad_info.max_salary
        if ad_info.description:
            ad.description = ad_info.description
        if ad_info.location:
            ad.location = ad_info.location
        if ad_info.status is not None:
            ad.status = ad_info.status

        position_title = ad.position_title
        min_salary = ad_info.min_salary
        max_salary = ad_info.max_salary
        description = ad.description
        location = ad.location
        status = ad.status
        s.commit()

    return {
        "position_title": position_title,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "description": description,
        "location": location,
        "status": status
    }


def get_company_all_ads_service():
    with Session() as session:
        ads = session.query(CompanyOffers).filter().all()

        return [CompanyAdModel(
            company_name=session.query(Companies).filter(Companies.id == ad.company_id).first().name,
            company_ad_id=str(ad.id),
            position_title=ad.position_title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location,
            status=ad.status
        ) for ad in ads]


def delete_company_ad_service(ad_id: uuid, user_id: uuid, company_name: str):
    with Session() as session:
        company_id = get_company_id_by_user_id_service(user_id)
        ad = session.query(CompanyOffers).filter(CompanyOffers.company_id == company_id,
                                                 CompanyOffers.id == ad_id).one()
        session.delete(ad)
        session.commit()
        return {'success': True}
