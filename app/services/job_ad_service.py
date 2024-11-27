from sqlalchemy.orm import Session
from fastapi import HTTPException
from HKS.data.models import CompanyOffers, Contacts
from HKS.data.schemas.contacts import ContactDetails


def add_or_validate_contact(db: Session, company_id: str, contact_data: ContactDetails):
    existing_contact = db.query(Contacts).filter(
        Contacts.company_id == company_id,
        Contacts.email == contact_data.email,
        Contacts.phone_number == contact_data.phone_number
    ).first()

    if existing_contact:
        return existing_contact.id

    new_contact = Contacts(
        company_id=company_id,
        email=contact_data.email,
        phone_number=contact_data.phone_number,
        web_page=contact_data.web_page,
        linkedin=contact_data.linkedin
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact.id
def create_new_ad_service(db: Session, company_id: str, ad_data: dict):
    contact_id = None
    if "contacts" in ad_data and ad_data["contacts"]:
        # Add or validate the contact
        contact_data = ad_data["contacts"]
        contact_id = add_or_validate_contact(
            db,
            company_id,
            contact_data
        )

    # Create the new ad
    new_ad = CompanyOffers(
        company_id=company_id,
        position_title=ad_data["position_title"],
        min_salary=ad_data["min_salary"],
        max_salary=ad_data["max_salary"],
        description=ad_data["description"],
        location=ad_data["location"],
        status=ad_data["status"],
        contacts_id=contact_id
    )
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad


def get_company_ads_service(db: Session, company_id: str):
    ads = db.query(CompanyOffers).filter(CompanyOffers.company_id == company_id).all()
    return ads


def update_company_ad_service(db: Session, ad_id: str, company_id: str, updated_data: dict):
    ad = db.query(CompanyOffers).filter(
        CompanyOffers.id == ad_id,
        CompanyOffers.company_id == company_id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    for key, value in updated_data.items():
        if hasattr(ad, key) and value is not None:
            setattr(ad, key, value)

    db.commit()
    db.refresh(ad)
    return ad
