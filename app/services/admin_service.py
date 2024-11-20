from sqlalchemy.orm import Session
from data.models import Professional, Companies, User
from common.responses import NotFound
from app.data.schemas.user_register import WaitingApproval
from data.schemas.professional import ProfessionalOut
from data.schemas.company import CompanyOut

def get_admin_by_id(id: int, db: Session) -> User:
    admin =  db.query(User).filter(User.id == id).first()
    if not admin:
        return None
    return admin

def approve_proffesional(id: int, db: Session):
    professional = db.query(Professional).filter(Professional.id == id).first()

    if professional:
        professional.is_approved = True
        db.commit()
        db.refresh(professional)
    else:
        return NotFound(content='Proffesional with ID {id} not found')
    
    
def approve_company(id: int, db: Session):
    company = db.query(Companies).filter(Companies.id == id).first()

    if company:
        company.is_approved = True
        db.commit()
        db.refresh(company)
    else:
        return NotFound(content='Company with ID {id} not found')
    

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


    

    
    

