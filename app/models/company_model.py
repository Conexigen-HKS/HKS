from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, event, Float
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


class CompanyBase(Base):
    __tablename__ = 'companies'
    company_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    company_username = Column(String, nullable=False, unique=True)
    company_hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_created_at = Column(DateTime, default=datetime.datetime.now)


class CompanyInfoBase(Base):
    __tablename__ = 'company_info'
    company_id = Column(Integer, ForeignKey('companies.company_id'), primary_key=True, nullable=False)
    company_name = Column(String, ForeignKey('companies.company_name'), nullable=False)
    company_description = Column(String)
    company_address = Column(String)


@event.listens_for(CompanyBase, 'after_insert')
def receive_after_insert(mapper, connection, target):
    metadata = MetaData()

    company_info_table = Table('company_info', metadata, autoload_with=connection)

    connection.execute(
        insert(company_info_table).values(
            company_id=target.company_id,
            company_name=target.company_name,
            company_description=""
        )
    )


class CompanyInfoModel(BaseModel):
    company_description: str
    company_address: str


class CompanyAdModel(BaseModel):
    position_title: str
    salary: float
    job_description: str


class CompanyAdBase(Base):
    __tablename__ = 'company_job_ad'
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    company_ad_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    position_title = Column(String)
    salary = Column(Float)
    job_description = Column(String)
    ad_created_at = Column(DateTime, default=datetime.datetime.now)
