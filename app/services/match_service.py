from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.data.models import Companies, Professional, RequestsAndMatches, ProfessionalProfile, CompanyOffers, User
#TODO - See bottom of the file.

def send_match_request(
    db: Session,
    target_id: str,
    current_user: User
):
    if current_user.role == 'professional':
        professional_profile = db.query(ProfessionalProfile).filter(
            ProfessionalProfile.user_id == current_user.id).first()

        if not professional_profile:
            raise HTTPException(status_code=404, detail='Professional profile not found')

        company_offer = db.query(CompanyOffers).filter(CompanyOffers.id == target_id).first()
        if not company_offer:
            raise HTTPException(status_code=404, detail='Company offer not found')

        existing_match = db.query(RequestsAndMatches).filter_by(
            professional_profile_id=professional_profile.id,
            company_offers_id=company_offer.id
        ).first()

        if existing_match:
            if not existing_match.match:
                existing_match.match = True
                db.commit()
                return {"message": "Match confirmed!"}
            else:
                return {"message": "Match already confirmed."}
        else:
            match_request = RequestsAndMatches(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
                match=False
            )
            db.add(match_request)
            db.commit()

            return {"message": "Match request sent successfully"}

    elif current_user.role == 'company':
        company_profile = db.query(Companies).filter(Companies.user_id == current_user.id).first()
        if not company_profile:
            raise HTTPException(status_code=404, detail="Company profile not found")

        professional_profile = db.query(ProfessionalProfile).filter(
            ProfessionalProfile.id == target_id
        ).first()
        if not professional_profile:
            raise HTTPException(status_code=404, detail='Professional profile not found')

        company_offer = db.query(CompanyOffers).filter(
            CompanyOffers.company_id == company_profile.id
        ).first()
        if not company_offer:
            raise HTTPException(status_code=404, detail='Company offer not found')

        existing_match = db.query(RequestsAndMatches).filter_by(
            professional_profile_id=professional_profile.id,
            company_offers_id=company_offer.id
        ).first()

        if existing_match:
            if not existing_match.match:
                existing_match.match = True
                db.commit()
                return {"message": "Match confirmed!"}
            else:
                return {"message": "Match already confirmed."}
        else:
            match_request = RequestsAndMatches(
                professional_profile_id=professional_profile.id,
                company_offers_id=company_offer.id,
                match=False
            )
            db.add(match_request)
            db.commit()

            return {"message": "Match request sent successfully"}

    else:
        raise HTTPException(status_code=403, detail="Invalid user role")


def view_matches(db: Session, current_user: User):
    try:
        if current_user.role == 'professional':
            professional_profile = db.query(ProfessionalProfile).filter(
                ProfessionalProfile.user_id == current_user.id
            ).first()

            if not professional_profile:
                raise HTTPException(
                    status_code=404,
                    detail="Professional profile not found"
                )

            matches = (
                db.query(RequestsAndMatches)
                .filter(
                    RequestsAndMatches.professional_profile_id == professional_profile.id                )
                .all()
            )

            if not matches:
                return {"matches": []}

            match_details = []
            for match in matches:
                company_offer = db.query(CompanyOffers).filter(
                    CompanyOffers.id == match.company_offers_id
                ).first()

                if company_offer:
                    match_details.append({
                        "match_id": str(match.company_offers_id),
                        "created_at": match.created_at,
                        "company_offer": {
                            "id": str(company_offer.id),
                            "min_salary": company_offer.min_salary,
                            "max_salary": company_offer.max_salary,
                            "status": company_offer.status
                        }
                    })

            return {"matches": match_details}

        elif current_user.role == 'company':
            company = db.query(Companies).filter(
                Companies.user_id == current_user.id
            ).first()

            if not company:
                raise HTTPException(
                    status_code=404,
                    detail="Company profile not found"
                )

            company_offers = db.query(CompanyOffers).filter(
                CompanyOffers.company_id == company.id
            ).all()

            if not company_offers:
                return {"matches": []}

            match_details = []
            for offer in company_offers:
                matches = (
                    db.query(RequestsAndMatches)
                    .filter(
                        RequestsAndMatches.company_offers_id == offer.id                    )
                    .all()
                )

                for match in matches:
                    prof_profile = db.query(ProfessionalProfile).filter(
                        ProfessionalProfile.id == match.professional_profile_id
                    ).first()

                    if prof_profile:
                        professional = db.query(Professional).filter(
                            Professional.id == prof_profile.professional_id
                        ).first()

                        if professional:
                            match_details.append({
                                "match_id": str(match.professional_profile_id),
                                "created_at": match.created_at,
                                "professional": {
                                    "id": str(professional.id),
                                    "first_name": professional.first_name,
                                    "last_name": professional.last_name,
                                    "status": professional.status
                                }
                            })

            return {"matches": match_details}

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

# Search with Thresholds (Should Have):

# Missing Functionality: Searches should support thresholds for salary ranges and skills (e.g., accepting matches that are not exact).
# Recommended Action: Enhance search endpoints to accept threshold parameters and adjust query logic accordingly.
# 
# 
# 
# Match Thresholds in Matching Logic (Should Have):

# Missing Functionality: Matching should consider thresholds for salary ranges and number of matching skills.
# Recommended Action: Update the matching services to include threshold logic as per the requirements.
