import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.data.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    author = relationship("User", foreign_keys=[author_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

class Requests(Base):
    __tablename__ = "requests"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    request_from = Column(String, nullable=False) # company/professional
    professional_profile_id = Column(UUID(as_uuid=True),ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
#ДА СЕ ДОБАВЯТ В PROFESSIONAL / COMPANIES - backpopulates връзки !
    professional = relationship("Professionals", foreign_keys=[professional_profile_id], back_populates="requests")
    company = relationship("Companies", foreign_keys=[company_offer_id], back_populates="requests")

class Matches(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True, nullable=False)
    professional_profile_id = Column(UUID(as_uuid=True),ForeignKey("professional_profile.id"))
    company_offer_id = Column(UUID(as_uuid=True), ForeignKey("company_offers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#ДА СЕ ДОБАВЯТ В PROFESSIONAL / COMPANIES - backpopulates връзки !
    professional = relationship("Professionals", foreign_keys=[professional_profile_id], back_populates="requests")
    company = relationship("Companies", foreign_keys=[company_offer_id], back_populates="requests")

class Requirements(Base):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True, nullable=False)
    description = Column(String,nullable=False)
#Да се добавят релации към Requirements / CompanyOffers в JobAdReq
    job_ad_reqs = relationship("JobAdReq", back_populates="requirement")
