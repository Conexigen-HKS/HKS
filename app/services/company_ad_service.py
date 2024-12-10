from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.data.schemas.company import CompanyAdModel, CompanyAdUpdateModel
from app.data.models import Companies, Location, User, CompanyOffers

#TODO - Implement a way for companies to add requirements with levels to their job ads.
#TODO - Add functionality to allow adding new skills/requirements and consider an approval workflow.
#NOTE - Status
# Active – visible
# Archived – matched with professional and no longer active

#WORKS
def create_new_ad(
    title: str,
    min_salary: int,
    max_salary: int,
    job_description: str,
    location: str,
    status: str,
    current_user: User,
    db: Session
) -> CompanyOffers:
    try:
        location_obj = db.query(Location).filter(Location.city_name.ilike(location)).first()
        if not location_obj:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found.")

        company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found.")

        new_ad = CompanyOffers(
            title=title,
            min_salary=min_salary,
            max_salary=max_salary,
            description=job_description,
            location_id=location_obj.id,
            status=status,
            company_id=company.id
        )

        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        return new_ad
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#WORKS
def get_company_ads(current_user: User, db: Session):
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

#WORKS
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


def delete_company_ad(ad_id: UUID, current_user: User, db: Session):
    company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail='Company not found.'
        )

    ad_to_delete = db.query(CompanyOffers).filter(
        CompanyOffers.id == ad_id,
        CompanyOffers.company_id == company.id
    ).first()

    if not ad_to_delete:
        raise HTTPException(
            status_code=404,
            detail='Ad not found.'
        )

    db.delete(ad_to_delete)
    db.commit()

    return {"detail": "Ad deleted successfully"}


def get_recent_job_ads(db: Session, limit: int = 5):
    job_ads = (
        db.query(CompanyOffers)
        .options(
            joinedload(CompanyOffers.company),  # Load related company data
            joinedload(CompanyOffers.location)  # Load location data
        )
        .filter(CompanyOffers.status == "Active")  # Filter only active ads
        .order_by(func.random())  # Sort by random ads
        .limit(limit)
        .all()
    )

    # Format the job ads for readability
    return [
        {
            "id": ad.id,
            "title": ad.title,
            "company_name": ad.company.name,
            "description": ad.description,
            "location_name": ad.location.city_name if ad.location else "N/A",
            "min_salary": ad.min_salary,
            "max_salary": ad.max_salary,
            "status": ad.status
        }
        for ad in job_ads
    ]


def get_spotlight_job_ad(db: Session):
    ad = (
        db.query(CompanyOffers)
        .options(
            joinedload(CompanyOffers.company),  # Load related company data
            joinedload(CompanyOffers.location)  # Load location data
        )
        .filter(CompanyOffers.status == "Active")  # Filter only active ads
        .order_by(func.random())  # Randomize the ad
        .first()
    )

    if not ad:
        return None

    return {
        "id": ad.id,
        "title": ad.title,
        "company_name": ad.company.name,
        "description": ad.description,
        "location_name": ad.location.city_name if ad.location else "N/A",
        "min_salary": ad.min_salary,
        "max_salary": ad.max_salary,
        "status": ad.status
    }
    return {"detail": "Ad deleted successfully"}
