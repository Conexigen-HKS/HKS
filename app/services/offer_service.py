from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.data.models import (
    Companies,
    CompanyOffers,
    Location,
    Professional,
    RequestsAndMatches,
    ProfessionalProfile,
    User
)
from app.services.job_app_service import get_all_job_applications_service
from app.services.mailjet_service import send_email


def send_offer_request(
        db: Session,
        professional_profile_id: str,
        current_user: User
):
    """
    target_id is user_id
    """
    if not current_user.role == 'company':
        raise HTTPException(
            status_code=403,
            detail='Only companies can send job offers.'
        )

    prof_profile = (
    db.query(ProfessionalProfile)
    .options(joinedload(ProfessionalProfile.professional))
    .filter(ProfessionalProfile.id == professional_profile_id)
    .first()
)
    if not prof_profile:
        raise HTTPException(
            status_code=404,
            detail='Professional profile not found'
        )
    professional = prof_profile.professional

    if professional.status == 'busy':
        raise HTTPException(
        status_code=400,
        detail='Professional is currently busy'
    )

    if not professional:
        raise HTTPException(
            status_code=404,
            detail='Professional not found.'
        )

    if professional.status == 'busy':
        raise HTTPException(
            status_code=400,
            detail='Professional is currently busy'
        )

    company = db.query(Companies).filter(Companies.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail='Company profile not found.'
        )
    company_id = company.id

    existing_confirmed_match = (
    db.query(RequestsAndMatches)
    .join(CompanyOffers, RequestsAndMatches.company_offers_id == CompanyOffers.id)
    .filter(
        RequestsAndMatches.professional_profile_id == prof_profile.id,
        CompanyOffers.company_id == company_id,
        RequestsAndMatches.match == True
    )
    .first()
)

    if not existing_confirmed_match:
        raise HTTPException(
            status_code=400,
            detail="No confirmed match exists with this professional."
        )

    company_offer = db.query(CompanyOffers).filter(
        CompanyOffers.id == existing_confirmed_match.company_offers_id
    ).first()

    if not company_offer:
        raise HTTPException(
            status_code=404,
            detail='Company offer details not found.'
        )
    
    company_offer.chosen_professional_offer_id=professional_profile_id
    db.commit()
    # СЕТВАМЕ ДА ИМА ИЗБРАН ПРОФЕСИОНАЛИСТ. АКО ПОЛУЧИМ ОТКАЗ ИЗЧИСТВАМЕ ПОЛЕТО И ОБЯВАТА ПРОДЪЛЖАВА ДА Е АКТИВНА
    #АКО ПОЛУЧИМ ПОТВЪРЖДЕНИЕ НА ОФЕРТАТА - ПОЛЕТО ОСТАВА ТАКА, ОБЯВАТА СТАВА matched

    job_description = company_offer.title
    salary_min = company_offer.min_salary
    salary_max = company_offer.max_salary
    job_summary = company_offer.description
    location = db.query(CompanyOffers).join(Location).filter(CompanyOffers.id == company_offer.id).first()
    location_name = location.location.city_name if location and location.location else "N/A"
    company_contact_email = company.email
    company_contact_phone = company.phone
    offer_id=company_offer.id

    subject = f"Job Offer from {company.name}"
    text_content = f"""
    Hello {professional.first_name} {professional.last_name},

    Congratulations! {company.name} has reviewed your profile and decided to extend a job offer to you.

    Here are the details of the offer:
    - **Position**: {job_description}
    - **Salary**: ${salary_min} - ${salary_max} annually
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
        <li><strong>Salary:</strong> ${salary_min} - ${salary_max} annually</li>
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
        html_content=html_content
    )

    return {"message": "Job offer sent successfully"}


def accept_offer(offer_id: str, db: Session, current_user: User):
    if current_user.role != 'professional':
        raise HTTPException(
            status_code=403,
            detail='This feature is available only for professionals'
        )

    professional_profiles = (
        db.query(ProfessionalProfile)
        .filter(ProfessionalProfile.user_id == current_user.id)
        .all()
    )

    if not professional_profiles:
        raise HTTPException(
            status_code=404,
            detail='Professional profiles not found.'
        )

    offer = (
        db.query(CompanyOffers)
        .filter(CompanyOffers.id == offer_id)
        .first()
    )
    if not offer:
        raise HTTPException(
            status_code=404,
            detail=f'Company offer with id{offer_id} not found.'
        )
    
    profile_ids = [profile.id for profile in professional_profiles]

    if offer.chosen_professional_offer_id not in profile_ids:
        raise HTTPException(
            status_code=400,
            detail='This offer is not made to you.'
        )
    
    professional_profile = next(
        (profile for profile in professional_profiles if profile.id == offer.chosen_professional_offer_id), None
    )

    if not professional_profile:
        raise HTTPException(
            status_code=404,
            detail='Professional profile associated with the offer not found.'
        )

    if offer.status == 'matched':
        raise HTTPException(
            status_code=400,
            detail='This offer has already been accepted by another professional.'
        )

    professional = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    if not professional:
        raise HTTPException(
            status_code=404,
            detail='Professional not found.'
        )
    professional.status = 'busy'
    professional_profile.chosen_company_offer_id = offer_id
    professional_profile.status = 'matched'
    offer.status = 'matched'
    offer.chosen_professional_offer_id = professional_profile.id

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail='An error occurred while accepting the offer.') from e

    return {"message": "Offer accepted successfully"}


def decline_offer(db: Session, current_user: User):
    if current_user.role != 'professional':
        raise HTTPException(
            status_code=403,
            detail='This feature is available only for professionals'
        )


def my_offers(db: Session, current_user: User):
    if current_user.role != 'professional':
        raise HTTPException(
            status_code=403,
            detail='This feature is available only for professionals'
        )


def company_sent_offers(db: Session, current_user: User):
    if current_user.role != 'company':
        raise HTTPException(
            status_code=403,
            detail='This feature is available only for companies.'
        )
    

def withdraw_offer(target_user: str, db: Session, current_user: User):
    if current_user.role != 'company':
        raise HTTPException(
            status_code=403,
            detail='This feature is available only for companies.'
        )
    
