from typing import List
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, event, Float
from sqlalchemy.sql import insert
from sqlalchemy import Table, MetaData
import datetime

Base = declarative_base()


class CompanyLoginModel(BaseModel):
    company_username: str
    password: str


class CompanyRegistrationModel(BaseModel):
    username: str
    password: str
    company_name: str


class CompanyInfoModel(BaseModel):
    company_description: str
    company_address: str
    company_contacts: str
    company_logo: str
    company_active_job_ads: int


class CompanyAdModel(BaseModel):
    company_ad_id: int | None = None
    position_title: str
    salary: float
    job_description: str
    location: str
    ad_status: int


class CompanyAdModel2(BaseModel):
    position_title: str
    salary: float
    job_description: str
    location: str
    ad_status: int
