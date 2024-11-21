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

    sent_messages = relationship("Message", foreign_keys="[Message.author_id]", back_populates="author", cascade="all, delete-orphan")
    receiver_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver", cascade="all, delete-orphan")
    professional = relationship("Professional", back_populates="user", uselist=False, cascade="all, delete-orphan")
    company = relationship("Companies", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Professional(Base):

    __tablename__ = "professionals"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    is_approved = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    address = Column(String(45), nullable=False)
    status = Column(String(45))
    summary = Column(String(255))
    picture = Column(String(255))

    user = relationship("User", back_populates="professional")
    professional_profile = relationship("ProfessionalProfile", back_populates="professional")


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

    professional = relationship("Professional", back_populates="professional_profile")
    chosen_offer = relationship("CompanyOffers", foreign_keys=[chosen_company_offer_id])
    skills = relationship("ProfessionalProfileSkills", back_populates="professional_profile")
    requests_and_matches = relationship("RequestsAndMatches", back_populates="professional_profile")


class ProfessionalProfileSkills(Base):
    __tablename__ = "professional_profile_skills"
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), primary_key=True)
    skills_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
    level = Column(Integer, nullable=True)

    professional_profile = relationship("ProfessionalProfile", back_populates="skills")
    skill = relationship("Skills", back_populates="professional_profile_skills")


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)

    professional_profile_skills = relationship("ProfessionalProfileSkills", back_populates="skill")


class Companies(Base):

    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    name = Column(String(45), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    contacts = Column(String, nullable=False)
    is_approved = Column(Boolean, default=False)

    user = relationship("User", back_populates="company", uselist=False)
    company_offers = relationship("CompanyOffers", back_populates="company")


class CompanyOffers(Base):
    __tablename__ = "company_offers"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    chosen_professional_offer_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    status = Column(String, nullable=True)

    company = relationship("Companies", back_populates="company_offers")
    requirements = relationship("CompaniesRequirements", back_populates="company_offer")
    requests_and_matches = relationship("RequestsAndMatches", back_populates="company_offer")


class CompaniesRequirements(Base):
    __tablename__ = "companies_requirements"
    title = Column(String, nullable=False)
    requirements_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
    company_offers_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), primary_key=True)
    level = Column(Integer, nullable=True)

    company_offer = relationship("CompanyOffers", back_populates="requirements")
    skill = relationship("Skills")


class RequestsAndMatches(Base):
    __tablename__ = "requests_and_matches"
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), primary_key=True)
    company_offers_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), primary_key=True)
    match = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    professional_profile = relationship("ProfessionalProfile", back_populates="requests_and_matches")
    company_offer = relationship("CompanyOffers", back_populates="requests_and_matches")


class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    author = relationship("User", foreign_keys=[author_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="receiver_messages")