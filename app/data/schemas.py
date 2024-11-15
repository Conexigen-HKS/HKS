import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Message Table
class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    author = relationship("UsersBase", foreign_keys=[author_id])
    receiver = relationship("UsersBase", foreign_keys=[receiver_id])


# Requests Table
class Requests(Base):
    __tablename__ = "requests"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    request_from = Column(String, nullable=False)  # company/professional
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.company_offers_id"), nullable=False)

    # Relationships
    professional = relationship("ProfessionalProfile", back_populates="requests")
    company_offer = relationship("CompanyOffersBase", back_populates="requests")


# Matches Table
class Matches(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.company_offers_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    professional = relationship("ProfessionalProfile", back_populates="matches")
    company_offer = relationship("CompanyOffersBase", back_populates="matches")


# Requirements Table
class Requirements(Base):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    description = Column(String, nullable=False)

    # Relationship to JobAdReq
    job_ad_reqs = relationship("JobAdReq", back_populates="requirement")


# Users Table
class UsersBase(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    user_username = Column(String, nullable=False, unique=True)
    user_hashed_password = Column(String, nullable=False)
    user_is_admin = Column(Integer, nullable=True, default=0)
    user_role = Column(String, nullable=True)
    user_created_at = Column(DateTime, default=func.now())

    # Relationship with ProfessionalProfile
    professional_profile = relationship("ProfessionalProfile", back_populates="user")


# Companies Table
class CompaniesBase(Base):
    __tablename__ = 'companies'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    company_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)

    # Relationships
    user = relationship('UsersBase', backref='company')


# Company Offers Table
class CompanyOffersBase(Base):
    __tablename__ = 'company_offers'
    company_offers_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)

    # Relationships
    company = relationship('CompaniesBase', back_populates='offers')
    requests = relationship("Requests", back_populates="company_offer")
    matches = relationship("Matches", back_populates="company_offer")
    job_ad_reqs = relationship("JobAdReq", back_populates="company_offer")
    chosen_by_professionals = relationship("ProfessionalProfile", back_populates="chosen_offer")


# Professional Profile Table
class ProfessionalProfile(Base):
    __tablename__ = 'professional_profile'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    professional_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    chosen_company_offer_id = Column(UUID(as_uuid=True), ForeignKey('company_offers.company_offers_id'))
    description = Column(String(255))
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    status = Column(String, nullable=False)

    # Relationships
    user = relationship("UsersBase", back_populates="professional_profile")
    chosen_offer = relationship("CompanyOffersBase", back_populates="chosen_by_professionals")
    job_app_skills = relationship("JobAppSkills", back_populates="professional_profile")
    requests = relationship("Requests", back_populates="professional")
    matches = relationship("Matches", back_populates="professional")


# Job Application Skills Table (Link between Professional Profile and Skills)
class JobAppSkills(Base):
    __tablename__ = 'job_app_skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    professional_offer_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=False)
    skills_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    level = Column(Integer, nullable=True)

    # Relationships
    skill = relationship("Skills", back_populates="job_app_skills")
    professional_profile = relationship("ProfessionalProfile", back_populates="job_app_skills")


# Skills Table
class Skills(Base):
    __tablename__ = 'skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)

    # Relationship with JobAppSkills (back_populates)
    job_app_skills = relationship("JobAppSkills", back_populates="skill")


# Job Ad Requirements Table (Link between Company Offers and Requirements)
class JobAdReq(Base):
    __tablename__ = 'job_ad_req'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_offers_id = Column(UUID(as_uuid=True), ForeignKey('company_offers.company_offers_id'), nullable=False)
    requirements_id = Column(UUID(as_uuid=True), ForeignKey('requirements.id'), nullable=False)
    level = Column(Integer, nullable=True)

    # Relationships
    requirement = relationship("Requirements", back_populates="job_ad_reqs")
    company_offer = relationship("CompanyOffersBase", back_populates="job_ad_reqs")
