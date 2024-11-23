from uuid import UUID
from sqlalchemy.orm import Session
from data.models import Professional, Companies, User
from common.responses import NotFound
from data.schemas.users import WaitingApproval
from data.schemas.professional import ProfessionalOut
from data.schemas.company import CompanyOut
from services.user_services import get_user_by_id, get_username_from_id, user_exists

from fastapi import HTTPException, status

def approve_user(id: str, entity_type: str, db: Session):
    if entity_type == 'professional':
        entity = db.query(Professional).filter(Professional.id == id).first()
    elif entity_type == 'company':
        entity = db.query(Companies).filter(Companies.id == id).first()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Entity type '{entity_type}' is not valid")

    if entity:
        entity.is_approved = True
        db.commit()
        db.refresh(entity)
        return entity
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_type.capitalize()} with ID {id} not found")
    

def waiting_approvals(db: Session) -> WaitingApproval:
    waiting_professionals = (
        db.query(Professional, User.username)
        .join(User, Professional.user_id == User.id)
        .filter(Professional.is_approved.is_(False))
        .all()
    )

    waiting_companies = (
        db.query(Companies, User.username)
        .join(User, Companies.user_id == User.id)
        .filter(Companies.is_approved.is_(False))
        .all()
    )

    professionals_out = [
        ProfessionalOut(
            id= professional.id,
            first_name = professional.first_name,
            last_name = professional.last_name,
            address = professional.address,
            is_approved = professional.is_approved,
            username=username
        )
        for professional, username in waiting_professionals
    ]

    company_out = [
       CompanyOut(
           id= company.id,
           name= company.name,
           address= company.address,
           description= company.description,
           contacts= company.contacts,
           is_approved= company.is_approved,
           username=username
       )
       for company, username in waiting_companies
   ]

    return WaitingApproval(professionals=professionals_out, companies=company_out)

def delete_user(id: str, db: Session):
    try:
        user_id = UUID(id)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID {id} not found"
            )
        
        db.delete(user)
        try:
            db.commit()
            return {"message": "User and related data deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Error while deleting user: {str(e)}"
            )
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid UUID format"
        )
    
def approve_requirement(id: str, db: Session, current_user: User):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not authorized.")
#COULD REQUIREMENTS - DA SE APPROVE REQUIREMENTS. TRQBVA DA SE DOBAQT PURVO V MODELS.
