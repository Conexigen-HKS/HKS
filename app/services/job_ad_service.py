from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.data.models import CompanyOffers, Contacts, Locations
from app.data.schemas.contacts import ContactDetails
from app.data.schemas.job_ad import CompanyAdModel2, CompanyAdModel
from app.services.company_service import get_company_id_by_user_id_service


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

def create_new_ad_service(
    db: Session,
    company_id: str,
    ad_data: dict
) -> CompanyOffers:
    try:
        # Validate location (do not create a new one)
        location_name = ad_data["location"]
        existing_location = db.query(Locations).filter(Locations.name == location_name).first()
        if not existing_location:
            raise HTTPException(
                status_code=400,
                detail=f"Location '{location_name}' does not exist. Please select an existing location."
            )

        contact_id = None
        if ad_data.get("contacts"):
            contact_data = ad_data["contacts"]
            contact_id = add_or_validate_contact(db, company_id, contact_data)
        else:
            company = db.query(Contacts).filter(Contacts.company_id == company_id).first()
            if company:
                contact_id = company.id

        new_ad = CompanyOffers(
            company_id=company_id,
            position_title=ad_data["position_title"],
            min_salary=ad_data["min_salary"],
            max_salary=ad_data["max_salary"],
            description=ad_data["description"],
            location=location_name,
            status=ad_data["status"],
        )
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        return new_ad
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating job ad: {str(e)}")



def get_company_ads_service(user_id: str):
    with Session() as session:
        company_id = get_company_id_by_user_id_service(user_id)
        ads = session.query(CompanyOffers).filter(CompanyOffers.company_id == company_id).all()
        return [CompanyAdModel(
            company_ad_id=str(ad.id),
            position_title=ad.position_title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location,
            status=ad.status
        ) for ad in ads]

def edit_company_ad_by_position_title_service(position_title: str, ad_info: CompanyAdModel2, user_id: str):
    with Session() as s:
        ad = s.query(CompanyOffers) \
            .filter(CompanyOffers.id == position_title,
                    CompanyOffers.company_id == get_company_id_by_user_id_service(user_id)) \
            .first()

        if not ad:
            raise HTTPException(
                status_code=404,
                detail="Ad not found"
            )
        if ad_info.position_title:
            ad.position_title = ad_info.position_title
        if ad_info.min_salary:
            ad.min_salary = ad_info.min_salary
        if ad_info.max_salary:
            ad.max_salary = ad_info.max_salary
        if ad_info.description:
            ad.description = ad_info.description
        if ad_info.location:
            ad.location = ad_info.location
        if ad_info.status is not None:
            ad.status = ad_info.status

        position_title = ad.position_title
        min_salary = ad_info.min_salary
        max_salary = ad_info.max_salary
        description = ad.description
        location = ad.location
        status = ad.status
        s.commit()

    return {
        "position_title": position_title,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "description": description,
        "location": location,
        "status": status
    }
