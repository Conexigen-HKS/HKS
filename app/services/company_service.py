from fastapi import Depends, HTTPException
from app.models.company_model import (CompanyBase, CompanyLoginModel,
                                      CompanyInfoBase, CompanyInfoModel,
                                      CompanyAdBase, CompanyAdModel)
from app.data.database import Session
import bcrypt


def create_new_company(username: str, password: str, company_name: str) -> CompanyBase:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_company = CompanyBase(
        company_username=username,
        company_hashed_password=hashed_password,
        company_name=company_name
    )

    with Session() as session:
        session.add(new_company)
        session.commit()

    return new_company


def company_login_service(company_login: CompanyLoginModel):
    with Session() as session:
        company_data = session.query(CompanyBase).filter(
            CompanyBase.company_username == company_login.company_username).first()
    if company_data is None or not bcrypt.checkpw(company_login.password.encode('utf-8'),
                                                  company_data.company_hashed_password.encode('utf-8')):
        return None
    return company_data


def edit_company_description_service(company_info: CompanyInfoModel, company_username: str):
    with Session() as s:
        company = s.query(CompanyBase).filter(CompanyBase.company_username == company_username).first()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        company_info_data = s.query(CompanyInfoBase).filter(CompanyInfoBase.company_id == company.company_id).first()

        if company_info_data is None:
            raise HTTPException(
                status_code=404,
                detail="Company information not found"
            )

        company_info_data.company_description = company_info.company_description
        if company_info.company_address:
            company_info_data.company_address = company_info.company_address
        s.commit()

        return {
            "company_name": company.company_name,
            "company_description": company_info_data.company_description,
            "company_address": company_info_data.company_address
        }


def create_new_ad_service(company_id: int, position_title: str, salary: float, job_description: str) -> CompanyAdBase:
    new_ad = CompanyAdBase(
        company_id=company_id,
        position_title=position_title,
        salary=salary,
        job_description=job_description
    )

    with Session() as session:
        session.add(new_ad)
        session.commit()

    return new_ad


def get_company_id_by_username_service(username: str) -> int:
    with Session() as session:
        try:
            company = session.query(CompanyBase).filter(CompanyBase.company_username == username).one()
            return company.company_id
        except:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
def get_company_name_by_username_service(username: str) -> str:
    with Session() as session:
        try:
            company = session.query(CompanyBase).filter(CompanyBase.company_username == username).one()
            return company.company_name
        except:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )