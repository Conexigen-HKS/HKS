"""
Match Service
In this file, we define the match service functions. We have two functions:
- send_match_request: This function is used to send a match request.
- view_matches: This function is used to view matches.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.data.models import (
    Companies,
    Professional,
    RequestsAndMatches,
    ProfessionalProfile,
    CompanyOffers,
    User,
)
from app.services.mailjet_service import send_email


def send_match_request(db: Session, target_id: str, current_user: User, profile_or_offer_id: str):
    """
    Send a match request
    :param db: Database session
    :param target_id: Target ID (company_offer_id or professional_profile_id depending on role)
    :param current_user: Current user
    :param profile_or_offer_id: The ID of the profile or offer from which the match request is sent
    :return: Match request
    """
    if current_user.role == "professional":
        professional_profile = (
            db.query(ProfessionalProfile)
            .filter(ProfessionalProfile.id == profile_or_offer_id)
            .first()
        )
        if not professional_profile:
            raise HTTPException(
                status_code=404, detail="Professional profile not found"
            )

        company_offer = (
            db.query(CompanyOffers).filter(CompanyOffers.id == target_id).first()
        )
        if not company_offer:
            raise HTTPException(status_code=404, detail="Company offer not found")

        existing_match = (
            db.query(RequestsAndMatches)
            .filter_by(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
            )
            .first()
        )

        if existing_match:
            if not existing_match.match:
                existing_match.match = True
                db.commit()

                company = db.query(Companies).filter(Companies.id == company_offer.company_id).first()
                if company and company.email:
                    subject = "New confirmed match"
                    text_content = f"Hello {company.name},\n\nYou have new confirmed match with {current_user.username}."
                    html_content = f"<p>Hello {company.name},</p><p>You have new confirmed match with {current_user.username}.</p>"
                    send_email(
                        to_email=company.email,
                        to_name=company.name,
                        subject=subject,
                        text_content=text_content,
                        html_content=html_content
                    )

                return {"message": "Match confirmed!"}
            else:
                return {"message": "Match already confirmed."}
        else:
            match_request = RequestsAndMatches(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
                match=False,
            )
            db.add(match_request)
            db.commit()

            company = db.query(Companies).filter(Companies.id == company_offer.company_id).first()
            if company and company.email:
                subject = "New match request"
                text_content = f"Hello {company.name},\n\nYou have new match request from {current_user.username}."
                html_content = f"<p>Hello {company.name},</p><p>You have new match request from {current_user.username}.</p>"
                send_email(
                    to_email=company.email,
                    to_name=company.name,
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content
                )

            return {"message": "Match request sent successfully"}

    elif current_user.role == "company":
        company_profile = (
            db.query(Companies).filter(Companies.user_id == current_user.id).first()
        )
        if not company_profile:
            raise HTTPException(status_code=404, detail="Company profile not found")

        professional_profile = (
            db.query(ProfessionalProfile)
            .filter(ProfessionalProfile.id == target_id)
            .first()
        )
        if not professional_profile:
            raise HTTPException(
                status_code=404, detail="Professional profile not found"
            )

        company_offer = (
            db.query(CompanyOffers)
            .filter(CompanyOffers.company_id == company_profile.id)
            .first()
        )
        if not company_offer:
            raise HTTPException(status_code=404, detail="Company offer not found")

        existing_match = (
            db.query(RequestsAndMatches)
            .filter_by(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
            )
            .first()
        )

        if existing_match:
            if not existing_match.match:
                existing_match.match = True
                db.commit()

                professional = db.query(Professional).filter(Professional.id == professional_profile.professional_id).first()
                if professional and professional.email:
                    subject = "New confirmed match"
                    text_content = f"Hello {professional.first_name},\n\nYou have new confirmed match with {company_profile.name}."
                    html_content = f"<p>Hello {professional.first_name},</p><p>You have new confirmed match with {company_profile.name}.</p>"
                    send_email(
                        to_email=professional.email,
                        to_name=f"{professional.first_name} {professional.last_name}",
                        subject=subject,
                        text_content=text_content,
                        html_content=html_content
                    )

                return {"message": "Match confirmed!"}
            else:
                return {"message": "Match already confirmed."}
        else:
            match_request = RequestsAndMatches(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
                match=False,
            )
            db.add(match_request)
            db.commit()

            professional = db.query(Professional).filter(Professional.id == professional_profile.professional_id).first()
            if professional and professional.email:
                subject = "New match request"
                text_content = f"Hello {professional.first_name},\n\nYou have new match request from {company_profile.name}."
                html_content = f"<p>Hello {professional.first_name},</p><p>You have new match request from {company_profile.name}.</p>"
                send_email(
                    to_email=professional.email,
                    to_name=f"{professional.first_name} {professional.last_name}",
                    subject=subject,
                    text_content=text_content,
                    html_content=html_content
                )
            return {"message": "Match request sent successfully"}


def view_matches(db: Session, current_user: User):
    """
    View matches
    :param db: Database session
    :param current_user: Current user
    :return: List of matches
    """
    try:
        if current_user.role == "professional":
            professional_profile = (
                db.query(ProfessionalProfile)
                .filter(ProfessionalProfile.user_id == current_user.id)
                .first()
            )

            if not professional_profile:
                raise HTTPException(
                    status_code=404, detail="Professional profile not found"
                )

            matches = (
                db.query(RequestsAndMatches)
                .filter(
                    RequestsAndMatches.professional_profile_id
                    == professional_profile.id
                )
                .all()
            )

            if not matches:
                return {"matches": []}

            match_details = []
            for match in matches:
                company_offer = (
                    db.query(CompanyOffers)
                    .filter(CompanyOffers.id == match.company_offers_id)
                    .first()
                )

                if company_offer:
                    match_details.append(
                        {
                            "match_id": str(match.company_offers_id),
                            "created_at": match.created_at,
                            "company_offer": {
                                "id": str(company_offer.id),
                                "min_salary": company_offer.min_salary,
                                "max_salary": company_offer.max_salary,
                                "status": company_offer.status,
                            },
                        }
                    )

            return {"matches": match_details}

        elif current_user.role == "company":
            company = (
                db.query(Companies).filter(Companies.user_id == current_user.id).first()
            )

            if not company:
                raise HTTPException(status_code=404, detail="Company profile not found")

            company_offers = (
                db.query(CompanyOffers)
                .filter(CompanyOffers.company_id == company.id)
                .all()
            )

            if not company_offers:
                return {"matches": []}

            match_details = []
            for offer in company_offers:
                matches = (
                    db.query(RequestsAndMatches)
                    .filter(RequestsAndMatches.company_offers_id == offer.id)
                    .all()
                )

                for match in matches:
                    prof_profile = (
                        db.query(ProfessionalProfile)
                        .filter(ProfessionalProfile.id == match.professional_profile_id)
                        .first()
                    )

                    if prof_profile:
                        professional = (
                            db.query(Professional)
                            .filter(Professional.id == prof_profile.professional_id)
                            .first()
                        )

                        if professional:
                            match_details.append(
                                {
                                    "match_id": str(match.professional_profile_id),
                                    "created_at": match.created_at,
                                    "professional": {
                                        "id": str(professional.id),
                                        "first_name": professional.first_name,
                                        "last_name": professional.last_name,
                                        "status": professional.status,
                                    },
                                }
                            )

            return {"matches": match_details}

        else:
            raise HTTPException(status_code=400, detail="Invalid role")

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e


def remove_job_offer(db: Session, target_id: str, current_user: User):
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Access forbidden for non-professionals")
    
    professional_profile = db.query(ProfessionalProfile).filter_by(user_id=current_user.id, status="active").first()
    if not professional_profile:
        raise HTTPException(status_code=404, detail="Active professional profile not found")
    
    company_offer = db.query(CompanyOffers).filter_by(id=target_id).first()
    if not company_offer:
        raise HTTPException(status_code=404, detail="Company offer not found")
    
    existing_entry = db.query(RequestsAndMatches).filter_by(
        professional_profile_id=professional_profile.id,
        company_offers_id=company_offer.id
    ).first()
    
    if existing_entry:
        db.delete(existing_entry)
        db.commit()
        return {"message": "Job ad dismissed successfully"}
    else:
        # Ако няма съществуваща запис, просто премахнете обявата от показването
        return {"message": "Job ad dismissed successfully"}