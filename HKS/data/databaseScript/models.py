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


class CompaniesBase(Base):
    __tablename__ = 'companies'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    company_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_name = Column(String, nullable=False, unique=True)
    company_description = Column(String, nullable=True)
    company_contacts = Column(String, nullable=True)
    user = relationship('UsersBase', backref='company')



class CompanyOffersBase(Base):
    __tablename__ = 'company_offers'
    company_offers_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'))
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    company_offers_col = Column(String)
    status = Column(String)
    company = relationship('CompaniesBase', backref='offers')


class CompanyRequirementsBase(Base):
    __tablename__ = 'company_requirements'
    company_requirements_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    min_experience = Column(Integer)
    max_experience = Column(Integer)



class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    message_content = Column(String, nullable=False)
    message_author_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    message_receiver_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    message_created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

# class Requests(Base):
#     __tablename__ = "requests"
#     request_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
#     request_from = Column(String, nullable=False) # company/professional
#     professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
#     company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
# #ДА СЕ ДОБАВЯТ В PROFESSIONAL / COMPANIES - backpopulates връзки !
#     professional = relationship("Professionals", foreign_keys=[professional_profile_id], back_populates="requests")
#     company = relationship("Companies", foreign_keys=[company_offer_id], back_populates="requests")
#

















# class Message(Base):
#     __tablename__ = "messages"
#     message_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
#     message_content = Column(String, nullable=False)
#     message_author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     message_receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     message_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#
#     author = relationship("UsersBase", foreign_keys=[message_author_id])
#     receiver = relationship("UsersBase", foreign_keys=[message_receiver_id])
#
# class Requests(Base):
#     __tablename__ = "requests"
#     request_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
#     request_from = Column(String, nullable=False) # company/professional
#     professional_profile_id = Column(UUID(as_uuid=True), ForeignKey("professional_profile.id"))
#     company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
# #ДА СЕ ДОБАВЯТ В PROFESSIONAL / COMPANIES - backpopulates връзки !
#     professional = relationship("Professionals", foreign_keys=[professional_profile_id], back_populates="requests")
#     company = relationship("Companies", foreign_keys=[company_offer_id], back_populates="requests")
#
# class Matches(Base):
#     __tablename__ = "matches"
#     match_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
#     professional_profile_id = Column(UUID(as_uuid=True),ForeignKey("professional_profile.id"))
#     company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
# #ДА СЕ ДОБАВЯТ В PROFESSIONAL / COMPANIES - backpopulates връзки !
#     professional = relationship("Professionals", foreign_keys=[professional_profile_id], back_populates="requests")
#     company = relationship("Companies", foreign_keys=[company_offer_id], back_populates="requests")
#
# class Requirements(Base):
#     __tablename__ = "requirements"
#     id = Column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True, nullable=False)
#     description = Column(String,nullable=False)
# #Да се добавят релации към Requirements / CompanyOffers в JobAdReq
#     job_ad_reqs = relationship("JobAdReq", back_populates="requirement")
