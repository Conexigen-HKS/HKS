"""
Company Ad Service
Methods for handling company job ads
"""

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.data.schemas.company import CompanyAdModel, CompanyAdUpdateModel
from app.data.models import (
    Companies,
    Location,
    User,
    CompanyOffers,
    CompaniesRequirements,
)
from app.services.skills_service import get_or_create_skill


def create_new_ad(
    title,
    min_salary,
    max_salary,
    job_description,
    location,
    status,
    current_user,
    db,
    skills,
):
    """
    Create a new job ad for the company
    :param title: Job title
    :param min_salary: Minimum salary
    :param max_salary: Maximum salary
    :param job_description: Job description
    :param location: Location of the job
    :param status: Job status
    :param current_user: Current user
    :param db: Database session
    :param skills: List of skills required for the job
    :return: Created job ad
    """
    try:
        # Look up the location by city name
        resolved_location = (
            db.query(Location).filter(Location.city_name.ilike(location)).first()
        )

        if not resolved_location:
            raise HTTPException(
                status_code=404, detail=f"Location '{location}' not found."
            )

        # Step 1: Create the job offer
        new_offer = CompanyOffers(
            title=title,
            company_id=current_user.company.id,  # Access the `id` of the company
            min_salary=min_salary,
            max_salary=max_salary,
            description=job_description,
            location_id=resolved_location.id,  # Use the resolved location ID
            status=status,
        )
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)

        # Step 2: Insert skills (requirements)
        for skill in skills:
            skill_entry = CompaniesRequirements(
                title=skill.name,
                requirements_id=get_or_create_skill(
                    skill.name, db
                ),  # Ensure skill ID resolver is functional
                company_offers_id=new_offer.id,
                level=skill.level,
            )
            db.add(skill_entry)

        db.commit()
        return new_offer

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while creating the job ad"
        )


def get_company_ads(current_user: User, db: Session):
    """
    Retrieve all job ads for the company
    :param current_user: Current user
    :param db: Database session
    :return: List of job ads
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
    Edit a company job ad by ID
    :param job_ad_id: Job ad ID
    :param ad_info: Job ad information
    :param current_company: Current company
    :param db: Database session
    :return: Updated job ad
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
        raise HTTPException(status_code=500, detail="Internal Server Error")


def delete_company_ad(ad_id: UUID, current_user: User, db: Session):
    """
    Delete a company job ad by ID
    :param ad_id: Job ad ID
    :param current_user: Current user
    :param db: Database session
    :return: Success message
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


def get_recent_job_ads(db: Session, limit: int = 5):
    """
    Retrieve a list of recent job ads
    :param db: Database session
    :param limit: Number of ads to retrieve
    :return: List of job ads
    """
    job_ads = (
        db.query(CompanyOffers)
        .options(
            joinedload(CompanyOffers.company),  # Load related company data
            joinedload(CompanyOffers.location),  # Load location data
            joinedload(CompanyOffers.requirements).joinedload(
                CompaniesRequirements.skill
            ),  # Load requirements and skills
        )
        .filter(CompanyOffers.status == "Active")  # Filter only active ads
        .order_by(func.random())  # Sort by random ads
        .limit(limit)
        .all()
    )

    return [
        {
            "id": ad.id,
            "title": ad.title,
            "company_name": ad.company.name,
            "description": ad.description,
            "location_name": ad.location.city_name if ad.location else "N/A",
            "min_salary": ad.min_salary,
            "max_salary": ad.max_salary,
            "status": ad.status,
            "skills": [
                {"name": requirement.skill.name, "level": requirement.level}
                for requirement in ad.requirements
            ],  # Extract skill names and levels from requirements
        }
        for ad in job_ads
    ]


def get_spotlight_job_ad(db: Session):
    """
    Retrieve a random job ad for the spotlight
    :param db: Database session
    :return: Job ad for the spotlight
    """
    ad = (
        db.query(CompanyOffers)
        .options(
            joinedload(CompanyOffers.company),  # Load related company data
            joinedload(CompanyOffers.location),  # Load location data
            joinedload(CompanyOffers.requirements).joinedload(
                CompaniesRequirements.skill
            ),  # Load requirements and skills
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
        "status": ad.status,
        "skills": [
            {"name": requirement.skill.name, "level": requirement.level}
            for requirement in ad.requirements
        ],  # Extract skill names and levels from requirements
    }
