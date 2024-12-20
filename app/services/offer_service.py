"""
This module contains the service functions for sending, accepting, declining, and withdrawing job offers.
"""
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.data.models import (
    Companies,
    CompanyOffers,
    Location,
    Professional,
    RequestsAndMatches,
    ProfessionalProfile,
    User,
)
from app.services.mailjet_service import send_email


def send_offer_request(
    db: Session, professional_profile_id: str, company_offer_id: str, current_user: User
):
    """
    Send a job offer to a professional.
    :param db: Database session
    :param professional_profile_id: Professional profile ID
    :param company_offer_id: Company offer ID
    :param current_user: Current user
    :return: Success message
    """
    if not current_user.role == "company":
        raise HTTPException(
            status_code=403, detail="Only companies can send job offers."
        )

    prof_profile = (
        db.query(ProfessionalProfile)
        .options(joinedload(ProfessionalProfile.professional))
        .filter(ProfessionalProfile.id == professional_profile_id)
        .first()
    )
    if not prof_profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    professional = prof_profile.professional

    if professional.status == "busy":
        raise HTTPException(status_code=400, detail="Professional is currently busy")

    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    if professional.status == "busy":
        raise HTTPException(status_code=400, detail="Professional is currently busy")

    company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found.")

    company_offer = (
        db.query(CompanyOffers)
        .filter(
            CompanyOffers.id == company_offer_id, CompanyOffers.company_id == company.id
        )
        .first()
    )
    if not company_offer:
        raise HTTPException(status_code=404, detail="Company offer not found.")

    existing_confirmed_match = (
        db.query(RequestsAndMatches)
        .filter(
            RequestsAndMatches.professional_profile_id == prof_profile.id,
            RequestsAndMatches.company_offers_id == company_offer.id,
            RequestsAndMatches.match == True,
        )
        .first()
    )
    if not existing_confirmed_match:
        raise HTTPException(
            status_code=400, detail="No confirmed match exists with this professional."
        )

    company_offer.chosen_professional_offer_id = professional_profile_id
    db.commit()

    job_description = company_offer.title
    salary_max = company_offer.max_salary
    job_summary = company_offer.description
    location = (
        db.query(CompanyOffers)
        .join(Location)
        .filter(CompanyOffers.id == company_offer.id)
        .first()
    )
    location_name = (
        location.location.city_name if location and location.location else "N/A"
    )
    company_contact_email = company.email
    company_contact_phone = company.phone
    offer_id = company_offer.id

    subject = f"Job Offer from {company.name}"
    text_content = f"""
    Hello {professional.first_name} {professional.last_name},

    Congratulations! {company.name} has reviewed your profile and decided to extend a job offer to you.

    Here are the details of the offer:
    - **Position**: {job_description}
    - **Salary**: ${salary_max}
    - **Location**: {location_name}
    - **Description**: {job_summary}

    If you have any questions or would like to accept this offer, feel free to contact us at:
    - Email: {company_contact_email}
    - Phone: {company_contact_phone}

    We look forward to hearing from you!

    Best regards,  
    {company.name} Team
    """

    html_content = f"""
    <p>Hello {professional.first_name} {professional.last_name},</p>
    <p>Congratulations! <strong>{company.name}</strong> has reviewed your profile and decided to extend a job offer to you.</p>

    <h3>Offer Details:</h3>
    <ul>
        <li><strong>Position:</strong> {job_description}</li>
        <li><strong>Salary:</strong> ${salary_max}</li>
        <li><strong>Location:</strong> {location_name}</li>
        <li><strong>Description:</strong> {job_summary}</li>
        <li><strong>OfferID:</strong> {offer_id}</li>
    </ul>

    <p>If you have any questions or would like to accept this offer, feel free to contact us at:</p>
    <ul>
        <li><strong>Email:</strong> {company_contact_email}</li>
        <li><strong>Phone:</strong> {company_contact_phone}</li>
    </ul>

    <p>We look forward to hearing from you!</p>
    <p>Best regards,<br><strong>{company.name} Team</strong></p>
    """

    send_email(
        to_email=professional.email,
        to_name=f"{professional.first_name} {professional.last_name}",
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )

    return {"message": "Job offer sent successfully"}


def accept_offer(company_offer_id: str, db: Session, current_user: User):
    """
    Accept an offer sent by the company.
    :param company_offer_id: Company offer ID
    :param db: Database session
    :param current_user: Current user
    :return: Success message
    """
    if current_user.role != "professional":
        raise HTTPException(
            status_code=403, detail="This feature is available only for professionals"
        )

    professional_profiles = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.user_id == current_user.id)
        .all()
    )

    if not professional_profiles:
        raise HTTPException(status_code=404, detail="Professional profiles not found.")

    offer = db.query(CompanyOffers).filter(CompanyOffers.id == company_offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=404,
            detail=f"Company offer with id {company_offer_id} not found.",
        )

    if offer.chosen_professional_offer_id not in [
        profile.id for profile in professional_profiles
    ]:
        raise HTTPException(
            status_code=400,
            detail="This offer is not made to you or is not valid for your profile.",
        )

    professional_profile = next(
        (
            profile
            for profile in professional_profiles
            if profile.id == offer.chosen_professional_offer_id
        ),
        None,
    )

    if not professional_profile:
        raise HTTPException(
            status_code=404,
            detail="Professional profile associated with the offer not found.",
        )

    if offer.status == "matched":
        raise HTTPException(
            status_code=400,
            detail="This offer has already been accepted by another professional.",
        )

    professional = (
        db.query(Professional).filter(Professional.user_id == current_user.id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    professional.status = "busy"
    professional_profile.chosen_company_offer_id = company_offer_id
    professional_profile.status = "matched"
    offer.status = "matched"
    offer.chosen_professional_offer_id = professional_profile.id

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while accepting the offer."
        ) from e

    return {"message": "Offer accepted successfully"}


def decline_offer(offer_id: str, db: Session, current_user: User):
    """
    Decline an offer sent by the company.
    :param offer_id: Offer ID
    :param db: Database session
    :param current_user: Current user
    :return: Success message
    """
    if current_user.role != "professional":
        raise HTTPException(
            status_code=403, detail="This feature is available only for professionals"
        )

    professional_profiles = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.user_id == current_user.id)
        .all()
    )

    if not professional_profiles:
        raise HTTPException(status_code=404, detail="Professional profiles not found.")

    offer = db.query(CompanyOffers).filter(CompanyOffers.id == offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=404, detail=f"Company offer with id{offer_id} not found."
        )

    profile_ids = [profile.id for profile in professional_profiles]

    if offer.chosen_professional_offer_id not in profile_ids:
        raise HTTPException(status_code=400, detail="This offer is not made to you.")

    professional_profile = next(
        (
            profile
            for profile in professional_profiles
            if profile.id == offer.chosen_professional_offer_id
        ),
        None,
    )

    if not professional_profile:
        raise HTTPException(
            status_code=404,
            detail="Professional profile associated with the offer not found.",
        )

    professional = (
        db.query(Professional).filter(Professional.user_id == current_user.id).first()
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    professional_profile.chosen_company_offer_id = None
    professional_profile.status = "active"
    offer.status = "active"
    offer.chosen_professional_offer_id = None

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while declining the offer."
        ) from e

    return {"message": "Offer declined successfully"}


def my_offers(db: Session, current_user: User):
    """
    Get all offers sent by the company.
    Return: List of offers
    """
    if current_user.role != "professional":
        raise HTTPException(
            status_code=403, detail="This feature is available only for professionals"
        )


def company_sent_offers(db: Session, current_user: User):
    """
    Get all offers sent by the company.
    Return: List of offers
    """
    if current_user.role != "company":
        raise HTTPException(
            status_code=403, detail="This feature is available only for companies."
        )


def withdraw_offer(target_user: str, db: Session, current_user: User):
    """
    Withdraw an offer sent by the company.
    :param target_user: User ID of the professional
    :param db: Database session"""
    if current_user.role != "company":
        raise HTTPException(
            status_code=403, detail="This feature is available only for companies."
        )
