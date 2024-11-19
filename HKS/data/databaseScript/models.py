import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UsersBase(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    user_username = Column(String, nullable=False, unique=True)
    user_hashed_password = Column(String, nullable=False)
    user_is_admin = Column(Integer, nullable=True, default=0)
    user_role = Column(String, nullable=True)
    user_created_at = Column(DateTime, default=func.now())
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey('professional_profile.id'), nullable=True)
    professional_profile = relationship('ProfessionalProfile', backref='users')


class CompaniesBase(Base):
    __tablename__ = 'companies'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    company_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)
    user = relationship('UsersBase', backref='company')


class ProfessionalProfile(Base):
    __tablename__ = 'professional_profile'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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


class CompanyOffersBase(Base):
    __tablename__ = 'company_offers'
    company_offers_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.company_id'), unique=True)
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)
    company = relationship('CompaniesBase', backref='offers')



class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    message_content = Column(String, nullable=False)
    message_author_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    message_receiver_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    message_created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)


class Requests(Base):
    __tablename__ = "requests"
    request_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    request_from = Column(String, nullable=False)  # company/professional
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.company_offers_id"), nullable=False)
    professional = relationship("ProfessionalProfile", foreign_keys=[professional_profile_id],
                                back_populates="requests")
    company = relationship("CompanyOffersBase", foreign_keys=[company_offer_id], back_populates="requests")


class Matches(Base):
    __tablename__ = "matches"
    match_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.company_offers_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    professional = relationship("ProfessionalProfile", foreign_keys=[professional_profile_id], back_populates="matches")
    company = relationship("CompanyOffersBase", foreign_keys=[company_offer_id], back_populates="matches")


class Requirements(Base):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    description = Column(String, nullable=False)
    job_ad_reqs = relationship("JobAdReq", back_populates="requirement")


class JobAppSkills(Base):
    __tablename__ = 'job_app_skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=False)
    skills_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    level = Column(Integer, nullable=True)

    # Relationships
    skill = relationship("Skills", back_populates="job_app_skills")
    professional_profile = relationship("ProfessionalProfile", back_populates="job_app_skills")


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    job_app_skills = relationship("JobAppSkills", back_populates="skill")


class JobAdReq(Base):
    __tablename__ = 'job_ad_req'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    company_offers_id = Column(UUID(as_uuid=True), ForeignKey('company_offers.company_offers_id'), nullable=False)
    requirements_id = Column(UUID(as_uuid=True), ForeignKey('requirements.id'), nullable=False)
    level = Column(Integer, nullable=True)

    # Relationships
    requirement = relationship("Requirements", back_populates="job_ad_reqs")
    company_offer = relationship("CompanyOffersBase", back_populates="job_ad_reqs")


class JobOffer(Base):
    __tablename__ = 'job_offers'
    id = Column(UUID(as_uuid=True), primary_key=True)
    company_offer_id = Column(UUID(as_uuid=True),
                              ForeignKey('company_offers.company_offers_id'))  # Reference the primary key
    company_offer = relationship("CompanyOffersBase")
