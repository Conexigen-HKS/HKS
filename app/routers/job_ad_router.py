from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from HKS.data.database import get_db
from HKS.data.models import CompanyOffers, User
from HKS.data.schemas.job_ad import CompanyAdModel, CompanyAdModel2
from app.common.auth import get_current_user
from app.services.job_ad_service import add_or_validate_contact

company_ad_router = APIRouter(prefix="/ads", tags=["Company Ads"])

@company_ad_router.post("/new_ad", response_model=CompanyAdModel)
def create_new_ad(company_ad: CompanyAdModel, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Only companies can create job ads")

    company_id = current_user.company.id

    contact_id = None
    if company_ad.contacts:
        contact_id = add_or_validate_contact(db, company_id, company_ad.contacts)

    new_ad = CompanyOffers(
        company_id=company_id,
        position_title=company_ad.position_title,
        min_salary=company_ad.min_salary,
        max_salary=company_ad.max_salary,
        description=company_ad.description,
        location=company_ad.location,
        status=company_ad.status,
        contacts_id=contact_id
    )
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)

    return CompanyAdModel(
        company_ad_id=str(new_ad.id),
        position_title=new_ad.position_title,
        min_salary=new_ad.min_salary,
        max_salary=new_ad.max_salary,
        description=new_ad.description,
        location=new_ad.location,
        status=new_ad.status,
        contacts=company_ad.contacts
    )


@company_ad_router.put("/ad/{ad_id}", response_model=CompanyAdModel2)
def update_company_ad(
    ad_id: str,
    ad_info: CompanyAdModel2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Only companies can update job ads")

    ad = db.query(CompanyOffers).filter(
        CompanyOffers.id == ad_id,
        CompanyOffers.company_id == current_user.company.id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    if ad_info.contacts:
        contact_id = add_or_validate_contact(db, ad.company_id, ad_info.contacts)
        ad.contacts_id = contact_id

    for key, value in ad_info.dict(exclude_unset=True).items():
        if key != "contacts":
            setattr(ad, key, value)

    db.commit()
    db.refresh(ad)

    return ad_info


@company_ad_router.put("/ad/{ad_id}", response_model=CompanyAdModel2)
def update_company_ad(ad_id: str, ad_info: CompanyAdModel2, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Only companies can update job ads")

    ad = db.query(CompanyOffers).filter(
        CompanyOffers.id == ad_id,
        CompanyOffers.company_id == current_user.company.id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    for key, value in ad_info.dict(exclude_unset=True).items():
        setattr(ad, key, value)

    db.commit()
    db.refresh(ad)

    return ad_info

@company_ad_router.get("/info", response_model=List[CompanyAdModel])
def get_company_ads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Only companies can view their ads")

    ads = db.query(CompanyOffers).filter(CompanyOffers.company_id == current_user.company.id).all()
    return [
        CompanyAdModel(
            company_ad_id=str(ad.id),
            position_title=ad.position_title,
            min_salary=ad.min_salary,
            max_salary=ad.max_salary,
            description=ad.description,
            location=ad.location,
            status=ad.status
        ) for ad in ads
    ]


@company_ad_router.put("/ad/{ad_id}", response_model=CompanyAdModel2)
def update_company_ad(ad_id: str, ad_info: CompanyAdModel2, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "company":
        raise HTTPException(status_code=403, detail="Only companies can update job ads")

    ad = db.query(CompanyOffers).filter(
        CompanyOffers.id == ad_id,
        CompanyOffers.company_id == current_user.company.id
    ).first()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

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
    if ad_info.status:
        ad.status = ad_info.status

    db.commit()
    db.refresh(ad)

    return ad_info