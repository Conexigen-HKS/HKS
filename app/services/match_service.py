from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from data.models import Companies, Professional, RequestsAndMatches, ProfessionalProfile, CompanyOffers, User

def send_match_request(
        db: Session,
        offer_id: str,
        current_user: User
        ):
    
    if current_user.role == 'professional':
        professional_profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.user_id == current_user.id).first()

        if not professional_profile:
            raise HTTPException(status_code=404, detail='Professional profile not found')
        
        company_offer = db.query(CompanyOffers).filter(CompanyOffers.id == offer_id).first()
        if not company_offer:
            raise HTTPException(status_code=404, detail='Company offer not found')
        
        match_request = RequestsAndMatches(
            professional_profile_id=professional_profile.id,
            company_offer_id=company_offer.id,
            match=False
        )
        db.add(match_request)
        db.commit()

        return {"message": "Match request sent successfully"}
    
    elif current_user.role == 'company':
        company_profile = db.query(Companies).filter(Companies.user_id == current_user.id).first()
        if not company_profile:
            raise HTTPException(status_code=404, detail="Company profile not found")
        
        company_offer = db.query(CompanyOffers).filter(CompanyOffers.id == offer_id).first()
        if not company_offer:
            raise HTTPException(status_code=404, detail="Company offer not found")

        professional_profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.id == company_offer.chosen_professional_offer_id).first()
        if not professional_profile:
            raise HTTPException(status_code=404, detail="Professional profile not found")
        
        match_request = RequestsAndMatches(
            professional_profile_id=professional_profile.id,
            company_offer_id=company_offer.id,
            match=False
        )
        db.add(match_request)
        db.commit()

        return {"message": "Match request sent successfully"}


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
                    RequestsAndMatches.professional_profile_id == professional_profile.id,
                    RequestsAndMatches.match == True
                )
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
                        RequestsAndMatches.company_offers_id == offer.id,
                        RequestsAndMatches.match == True
                    )
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
