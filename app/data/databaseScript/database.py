from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, BigInteger, func
import uuid
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()



class Company(Base):
    __tablename__ = 'Companies'
    company_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)


class User(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_username = Column(String, nullable=False, unique=True)
    user_hashed_password = Column(String, nullable=False)
    user_is_admin = Column(Integer, nullable=True, default=0)
    user_role = Column(String, nullable=True)
    user_created_at = Column(DateTime, default=func.now())


class CompanyOffers(Base):
    __tablename__ = 'Company_offers'
    company_offers_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)


class CompanyRequirements(Base):
    __tablename__ = 'Company_requirements'
    company_requirements_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    min_experience = Column(Integer)
    max_experience = Column(Integer)

def create_postgresql_file():
    User()
    Company()
    CompanyOffers()
    CompanyRequirements()