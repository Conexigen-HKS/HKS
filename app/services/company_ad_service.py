"""
Company Ad Service
In this file, we define the company ad service module.
This module contains helper functions for creating, updating, and deleting company ads.
Functions:
- create_new_ad: This function creates a new company ad.
- get_company_ads: This function gets all company ads.
- edit_company_ad_by_id: This function edits a company ad by ID.
- delete_company_ad: This function deletes a company ad.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.data.models import Companies, CompanyOffers, Location, User
from app.data.schemas.company import CompanyAdModel, CompanyAdUpdateModel

# TODO - Implement a way for companies to add requirements with levels to their job ads.
# TODO - Add functionality to allow adding new skills/requirements and consider an approval workflow.
# NOTE - Status
# Active – visible
# Archived – matched with professional and no longer active


def create_new_ad(
    title: str,
    min_salary: int,
    max_salary: int,
    job_description: str,
    location: str,
    status: str,
    current_user: User,
    db: Session,
) -> CompanyOffers:
    """
    Create a new company ad
    :param title: The title of the ad
    :param min_salary: The minimum salary of the ad
    :param max_salary: The maximum salary of the ad
    :param job_description: The job description of the ad
    :param location: The location of the ad
    :param status: The status of the ad
    :param current_user: The current
    :param db: The database session
    :return: The new company ad
    """
    try:
        location_obj = (
            db.query(Location).filter(Location.city_name.ilike(location)).first()
        )
        if not location_obj:
            raise HTTPException(
                status_code=404, detail=f"Location '{location}' not found."
            )

        company = (
            db.query(Companies).filter(Companies.user_id == current_user.id).first()
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found.")

        new_ad = CompanyOffers(
            title=title,
            min_salary=min_salary,
            max_salary=max_salary,
            description=job_description,
            location_id=location_obj.id,
            status=status,
            company_id=company.id,
        )

        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        return new_ad
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def get_company_ads(current_user: User, db: Session):
    """
    Get all company ads
    :param current_user: The current
    :param db: The database session
    :return: A list of company ads
    """
    company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
    company_ads = (
        db.query(CompanyOffers).filter(CompanyOffers.company_id == company.id).all()
    )

    return [
        CompanyAdModel(
            company_name=company.name,
            company_ad_id=ad.id,
            title=ad.title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location.city_name,
            status=ad.status,
        )
        for ad in company_ads
    ]


def edit_company_ad_by_id(
    job_ad_id: str, ad_info: CompanyAdUpdateModel, current_company: User, db: Session
) -> CompanyAdModel:
    """
    Edit a company ad by ID
    :param job_ad_id: The ID of the ad
    :param ad_info: The ad information
    :param current_company: The current company
    :param db: The database session
    :return: The updated company ad
    """
    try:
        company = (
            db.query(Companies).filter(Companies.user_id == current_company.id).first()
        )
        company_ad = (
            db.query(CompanyOffers).filter(CompanyOffers.id == job_ad_id).first()
        )
        if not company_ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        if ad_info.title is not None:
            company_ad.title = ad_info.title
        if ad_info.min_salary is not None:
            company_ad.min_salary = ad_info.min_salary
        if ad_info.max_salary is not None:
            company_ad.max_salary = ad_info.max_salary
        if ad_info.description is not None:
            company_ad.description = ad_info.description
        if ad_info.location is not None:
            location_obj = (
                db.query(Location)
                .filter(Location.city_name.ilike(ad_info.location))
                .first()
            )
            if not location_obj:
                raise HTTPException(
                    status_code=404, detail=f"Location '{ad_info.location}' not found."
                )
            company_ad.location_id = location_obj.id
        if ad_info.status is not None:
            company_ad.status = ad_info.status

        db.commit()
        db.refresh(company_ad)

        location_name = (
            location_obj.city_name
            if ad_info.location
            else company_ad.location.city_name
        )

        response = CompanyAdModel(
            company_name=company.name,
            company_ad_id=company_ad.id,
            title=company_ad.title,
            min_salary=company_ad.min_salary,
            max_salary=company_ad.max_salary,
            description=company_ad.description,
            location=location_name,
            status=company_ad.status,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def delete_company_ad(ad_id: UUID, current_user: User, db: Session):
    """
    Delete a company ad
    :param ad_id: The ID of the ad
    :param current_user: The current
    :param db: The database session
    :return: The deletion message
    """
    company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")

    ad_to_delete = (
        db.query(CompanyOffers)
        .filter(CompanyOffers.id == ad_id, CompanyOffers.company_id == company.id)
        .first()
    )

    if not ad_to_delete:
        raise HTTPException(status_code=404, detail="Ad not found.")

    db.delete(ad_to_delete)
    db.commit()

    return {"detail": "Ad deleted successfully"}
