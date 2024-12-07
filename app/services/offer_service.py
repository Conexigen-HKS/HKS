from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.data.models import (
    Companies,
    CompanyOffers,
    Location,
    RequestsAndMatches,
    ProfessionalProfile,
    User
)
from app.services.mailjet_service import send_email


def send_offer_request(
        db: Session,
        target_id: str,
        current_user: User
):
    if not current_user.role == 'company':
        raise HTTPException(
            status_code=403,
            detail='Only companies can send job offers.'
        )

    prof_profile = (
    db.query(ProfessionalProfile)
    .options(joinedload(ProfessionalProfile.professional))
    .filter(ProfessionalProfile.user_id == target_id)
    .first()
)
    if not prof_profile:
        raise HTTPException(
            status_code=404,
            detail='Professional profile not found'
        )
    professional = prof_profile.professional

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
        RequestsAndMatches.match == True # is ili == ?
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
    
    company_offer.chosen_professional_offer_id = prof_profile.id

    job_description = company_offer.title
    salary_min = company_offer.min_salary
    salary_max = company_offer.max_salary
    job_summary = company_offer.description
    location = db.query(CompanyOffers).join(Location).filter(CompanyOffers.id == company_offer.id).first()
    location_name = location.location.city_name if location and location.location else "N/A"
    company_contact_email = company.email
    company_contact_phone = company.phone

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

def accept_offer():
    pass