from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from data.models import Location, Companies, User, CompanyOffers
from data.schemas.company import CompanyAdModel, CompanyOut, CompanyResponse


def show_company_description(user: User, db: Session):
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