from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy import func
from app.data.schemas.company import (CompanyAdUpdateModel, CompanyInfoModel,CompanyAdModel, CompanyAdModel2, ShowCompanyModel)
from app.data.models import Companies, Location, User, CompanyOffers
# from app.services.company_service import get_company_id_by_user_id_service, get_company_name_by_username_service


def create_new_ad_service(company_id: str, title: str,
                          min_salary: int, max_salary: int, job_description: str,
                          location: str, status: str, db: Session) -> CompanyOffers:
    try:
        # Lookup the Location by city_name
        location_obj = db.query(Location).filter(Location.city_name.ilike(location)).first()
        if not location_obj:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found.")

        new_ad = CompanyOffers(
            company_id=str(company_id),
            title=title,
            min_salary=min_salary,
            max_salary=max_salary,
            description=job_description,
            location_id=location_obj.id,
            status=status
        )

        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        return new_ad
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_company_ads_service(current_user: User, db: Session):
        company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
        company_ads = db.query(CompanyOffers).filter(CompanyOffers.company_id == company.id).all()

        return [
        CompanyAdModel(
            company_name=company.name,
            company_ad_id=ad.id,
            title=ad.title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location.city_name,
            status=ad.status
        )
        for ad in company_ads
    ]

def edit_company_ad_by_id(
        job_ad_id: str,
        ad_info: CompanyAdUpdateModel,
        current_company: User, 
        db: Session
    )-> CompanyAdModel:
    try:
        company = db.query(Companies).filter(Companies.user_id == current_company.id).first()
        company_ad = db.query(CompanyOffers).filter(CompanyOffers.id == job_ad_id).first()
        if not company_ad:
            raise HTTPException(
                status_code=404,
                detail="Ad not found"
            )
        if ad_info.title is not None:
            company_ad.title = ad_info.title
        if ad_info.min_salary is not None:
            company_ad.min_salary = ad_info.min_salary
        if ad_info.max_salary is not None:
            company_ad.max_salary = ad_info.max_salary
        if ad_info.description is not None:
            company_ad.description = ad_info.description
        if ad_info.location is not None:
            location_obj = db.query(Location).filter(Location.city_name.ilike(ad_info.location)).first()
            if not location_obj:
                raise HTTPException(status_code=404, detail=f"Location '{ad_info.location}' not found.")
            company_ad.location_id = location_obj.id
        if ad_info.status is not None:
            company_ad.status = ad_info.status

        db.commit()
        db.refresh(company_ad)
        
        location_name = location_obj.city_name if ad_info.location else company_ad.location.city_name

        response = CompanyAdModel(
            company_name=company.name,
            company_ad_id=company_ad.id,
            title=company_ad.title,
            min_salary=company_ad.min_salary,
            max_salary=company_ad.max_salary,
            description=company_ad.description,
            location=location_name,
            status=company_ad.status
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# def get_company_all_ads_service():
#     with Session() as session:
#         ads = session.query(CompanyOffers).filter().all()

#         return [CompanyAdModel(
#             company_name=session.query(Companies).filter(Companies.id == ad.company_id).first().name,
#             company_ad_id=str(ad.id),
#             position_title=ad.position_title,
#             min_salary=ad.min_salary,
#             max_salary=ad.max_salary,
#             description=ad.description,
#             location=ad.location,
#             status=ad.status
#         ) for ad in ads]


# def delete_company_ad_service(ad_id: uuid, user_id: uuid, company_name: str):
#     with Session() as session:
#         company_id = get_company_id_by_user_id_service(user_id)
#         ad = session.query(CompanyOffers).filter(CompanyOffers.company_id == company_id,
#                                                  CompanyOffers.id == ad_id).one()
#         session.delete(ad)
#         session.commit()
#         return {'success': True}
