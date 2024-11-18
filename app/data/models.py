import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()
 
 
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
 
    sent_messages = relationship("Message", foreign_keys="[Message.author_id]", back_populates="author")
    receiver_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")
    professional_profile = relationship("ProfessionalProfile", uselist=False,
                                        back_populates="user")  # Set `uselist=False` for one-to-one
 
 
class Professional(Base):
    __tablename__ = "professionals"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
 
 
class ProfessionalProfile(Base):
    __tablename__ = 'professional_profile'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    professional_id = Column(UUID(as_uuid=True), ForeignKey('professionals.id'), nullable=False)
    chosen_company_offer_id = Column(UUID(as_uuid=True), ForeignKey('company_offers.id'))
    description = Column(String(255))
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    status = Column(String, nullable=False)
 
    user = relationship("User", back_populates="professional_profile")
    # Define a unidirectional relationship with CompanyOffers
    chosen_offer = relationship("CompanyOffers", foreign_keys=[chosen_company_offer_id])
    job_app_skills = relationship("JobAppSkills", back_populates="professional_profile")
    requests = relationship("Requests", back_populates="professional")
    matches = relationship("Matches", back_populates="professional")
 
 
class Companies(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    name = Column(String(45), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    contacts = Column(String, nullable=False)
    is_approved = Column(Boolean, default=False)
 
    requests = relationship("Requests", back_populates="company")
 
class CompanyOffers(Base):
    __tablename__ = "company_offers"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    choosen_professional_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
 
    matches = relationship("Matches", back_populates="company_offer")
    job_ad_reqs = relationship("JobAdReq", back_populates="company_offer")
 
 
 
class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
 
    author = relationship("User", foreign_keys=[author_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="receiver_messages")
 
 
class Requests(Base):
    __tablename__ = "requests"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    request_from = Column(String, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)  # Add this foreign key
 
    professional = relationship("ProfessionalProfile", foreign_keys=[professional_profile_id],
                                back_populates="requests")
    company = relationship("Companies", back_populates="requests", foreign_keys=[company_id])  # Set up the relationship with Companies
 
 
class Matches(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
 
    professional = relationship("ProfessionalProfile", foreign_keys=[professional_profile_id], back_populates="matches")
    company_offer = relationship("CompanyOffers", foreign_keys=[company_offer_id], back_populates="matches")
 
 
class Requirements(Base):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
 
    job_ad_reqs = relationship("JobAdReq", back_populates="requirement")
 
 
class JobAdReq(Base):
    __tablename__ = 'job_ad_req'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_offers_id = Column(UUID(as_uuid=True), ForeignKey('company_offers.id'), nullable=False)
    requirements_id = Column(UUID(as_uuid=True), ForeignKey('requirements.id'), nullable=False)
    level = Column(Integer, nullable=True)
 
    requirement = relationship("Requirements", back_populates="job_ad_reqs")
    company_offer = relationship("CompanyOffers", back_populates="job_ad_reqs")
 
 
class JobAppSkills(Base):
    __tablename__ = 'job_app_skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    professional_offer_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=False)
    skills_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    level = Column(Integer, nullable=True)
 
    skill = relationship("Skills", back_populates="job_app_skills")
    professional_profile = relationship("ProfessionalProfile", back_populates="job_app_skills")
 
 
class Skills(Base):
    __tablename__ = 'skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
 
    job_app_skills = relationship("JobAppSkills", back_populates="skill")
 