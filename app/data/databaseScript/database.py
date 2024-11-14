
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UsersBase(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_username = Column(String, nullable=False, unique=True)
    user_hashed_password = Column(String, nullable=False)
    user_is_admin = Column(Integer, nullable=True, default=0)
    user_role = Column(String, nullable=True)
    user_created_at = Column(DateTime, default=func.now())


class CompaniesBase(Base):
    __tablename__ = 'Companies'
    user_id = Column(Integer, ForeignKey('Users.user_id'))  # One-to-one relationship
    company_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)
    user = relationship(UsersBase, backref='company')  # Changed 'UserBase' to UsersBase


class CompanyOffersBase(Base):
    __tablename__ = 'Company_offers'
    company_offers_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey('Companies.company_id'))  # One-to-many relationship
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)
    company = relationship(CompaniesBase, backref='offers')  # Relationship field


class CompanyRequirementsBase(Base):
    __tablename__ = 'Company_requirements'
    company_requirements_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    min_experience = Column(Integer)
    max_experience = Column(Integer)

def create_postgresql_file():
    UsersBase()
    CompaniesBase()
    CompanyOffersBase()
    CompanyRequirementsBase()