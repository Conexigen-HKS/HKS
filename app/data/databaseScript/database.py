from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, BigInteger, func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserBase(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    user_username = Column(String, nullable=False, unique=True)
    user_hashed_password = Column(String, nullable=False)
    user_is_admin = Column(Integer, nullable=True, default=0)
    user_role = Column(String, nullable=True)
    user_created_at = Column(DateTime, default=func.now())


class CompanyBase(Base):
    __tablename__ = 'Companies'
    user_id = Column(Integer, ForeignKey('Users.user_id'))  # One-to-one relationship
    company_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)
    user = relationship('UserBase', backref='company')  # Relationship field


class CompanyOffersBase(Base):
    __tablename__ = 'Company_offers'
    company_offers_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey('Companies.company_id'))  # One-to-many relationship
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)
    company = relationship('CompanyBase', backref='offers')  # Relationship field


class CompanyRequirementsBase(Base):
    __tablename__ = 'Company_requirements'
    company_requirements_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    min_experience = Column(Integer)
    max_experience = Column(Integer)


def create_postgresql_file():
    UserBase()
    CompanyBase()
    CompanyOffersBase()
    CompanyRequirementsBase()
