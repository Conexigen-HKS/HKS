import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    User model
    Attributes:
    - id: UUID, primary key
    - username: String, unique, not nullable
    - hashed_password: String, not nullable
    - is_admin: Boolean, default False
    - role: String, not nullable
    - created_at: DateTime, not nullable
    """
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sent_messages = relationship(
        "Message",
        foreign_keys="[Message.author_id]",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    receiver_messages = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    professional = relationship(
        "Professional",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    company = relationship(
        "Companies", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Professional(Base):
    """
    Professional model
    Attributes:
    - id: UUID, primary key
    - is_approved: Boolean, default False
    - user_id: UUID, foreign key, not nullable
    - first_name: String, not nullable
    - last_name: String, not nullable
    - location_id: Integer, foreign key
    """
    __tablename__ = "professionals"
    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False
    )
    is_approved = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String(45), default="Active")
    summary = Column(String(255))
    picture = Column(String(255))
    phone = Column(String(15), nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    website = Column(String(255), nullable=True, unique=True)

    user = relationship("User", back_populates="professional")
    professional_profile = relationship(
        "ProfessionalProfile", back_populates="professional"
    )
    location = relationship("Location", back_populates="professionals")


class ProfessionalProfile(Base):
    """
    Professional Profile model
    Attributes:
    - id: UUID, primary key
    - user_id: UUID, foreign key, not nullable
    - professional_id: UUID, foreign key, not nullable
    - chosen_company_offer_id: UUID, foreign key
    - description: String, nullable
    - min_salary: Integer
    - max_salary: Integer
    - status: String, not nullable
    - location_id: Integer, foreign key, not nullable
    """
    __tablename__ = "professional_profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("professionals.id"), nullable=False
    )
    chosen_company_offer_id = Column(
        UUID(as_uuid=True), ForeignKey("company_offers.id")
    )
    description = Column(String(255))
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    status = Column(
        String, nullable=False
    )  # ("Active", "Hidden", "Private", "Matched")
    location_id = Column(
        Integer, ForeignKey("locations.id"), nullable=False
    )

    location = relationship(
        "Location", back_populates="professional_profiles"
    )
    professional = relationship("Professional", back_populates="professional_profile")
    chosen_offer = relationship("CompanyOffers", foreign_keys=[chosen_company_offer_id])
    skills = relationship(
        "ProfessionalProfileSkills",
        back_populates="professional_profile",
        cascade="all, delete-orphan",
    )
    requests_and_matches = relationship(
        "RequestsAndMatches", back_populates="professional_profile", cascade="all, delete-orphan"
    )


class ProfessionalProfileSkills(Base):
    """
    Professional Profile Skills model
    Attributes:
    - professional_profile_id: UUID, foreign key, primary key
    - skills_id: UUID, foreign key, primary key
    - level: String, nullable
    """
    __tablename__ = "professional_profile_skills"
    professional_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profile.id"), primary_key=True
    )
    skills_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
    level = Column(String, nullable=True)

    professional_profile = relationship("ProfessionalProfile", back_populates="skills")
    skill = relationship("Skills", back_populates="professional_profile_skills")


class Skills(Base):
    """
    Skills model
    Attributes:
    - id: UUID, primary key
    - name: String, not nullable
    """
    __tablename__ = "skills"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = Column(String(255), nullable=False)

    professional_profile_skills = relationship(
        "ProfessionalProfileSkills", back_populates="skill"
    )


class Companies(Base):
    """
    Companies model
    Attributes:
    - id: UUID, primary key
    - user_id: UUID, foreign key, not nullable
    - name: String, unique, not nullable
    - location_id: Integer, foreign key, nullable
    - description: String, not nullable
    - contacts: String, not nullable
    - is_approved: Boolean, default False
    - picture: String, nullable
    - phone: String, nullable, unique
    - email: String, nullable, unique
    - website: String, nullable, unique
    - status: String, not nullable, default "Active"
    """
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(45), unique=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))
    description = Column(String(255), nullable=False)
    contacts = Column(String, nullable=False)
    is_approved = Column(Boolean, default=False)
    picture = Column(String(255))
    phone = Column(String(15), nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    website = Column(String(255), nullable=True, unique=True)
    status = Column(String(45), default="Active")


    user = relationship("User", back_populates="company", uselist=False)
    company_offers = relationship("CompanyOffers", back_populates="company")
    location = relationship("Location", back_populates="companies")  # NEW


class CompanyOffers(Base):
    """
    Company Offers model
    Attributes:
    - id: UUID, primary key
    - title: String, not nullable
    - company_id: UUID, foreign key, not nullable
    - chosen_professional_offer_id: UUID, foreign key, nullable
    - min_salary: Integer, nullable
    - max_salary: Integer, nullable
    - description: String, not nullable
    - location_id: Integer, foreign key, nullable
    - status: String, nullable
    """
    __tablename__ = "company_offers"
    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False
    )
    title = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    chosen_professional_offer_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profile.id"), nullable=True
    )
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    description = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)  # NEW
    status = Column(String, nullable=True)

    company = relationship("Companies", back_populates="company_offers")
    location = relationship("Location", back_populates="company_offers")  # NEW
    requirements = relationship("CompaniesRequirements", back_populates="company_offer")
    requests_and_matches = relationship(
        "RequestsAndMatches", back_populates="company_offer",cascade="all, delete"
    )


class CompaniesRequirements(Base):
    """
    Companies Requirements model
    Attributes:
    - title: String, not nullable
    - requirements_id: UUID, foreign key, primary key
    - company_offers_id: UUID, foreign key, primary key
    - level: Integer, nullable
    """
    __tablename__ = "companies_requirements"
    title = Column(String, nullable=False)
    requirements_id = Column(
        UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True
    )
    company_offers_id = Column(
        UUID(as_uuid=True), ForeignKey("company_offers.id"), primary_key=True
    )
    level = Column(String, nullable=True)

    company_offer = relationship("CompanyOffers", back_populates="requirements")
    skill = relationship("Skills")


class RequestsAndMatches(Base):
    """
    Requests and Matches model
    Attributes:
    - professional_profile_id: UUID, foreign key, primary key
    - company_offers_id: UUID, foreign key, primary key
    - match: Boolean, default False
    - created_at: DateTime, not nullable
    """
    __tablename__ = "requests_and_matches"
    professional_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("professional_profile.id", ondelete="CASCADE"), primary_key=True
    )
    company_offers_id = Column(
        UUID(as_uuid=True),
        ForeignKey("company_offers.id", ondelete="CASCADE"),
        primary_key=True
    )
    match = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    professional_profile = relationship(
        "ProfessionalProfile", back_populates="requests_and_matches", passive_deletes=True
    )
    company_offer = relationship("CompanyOffers", back_populates="requests_and_matches")


class Message(Base):
    """
    Message model
    Attributes:
    - id: UUID, primary key
    - content: String, not nullable
    - author_id: UUID, foreign key, not nullable
    - receiver_id: UUID, foreign key, not nullable
    - created_at: DateTime, not nullable
    """
    __tablename__ = "messages"
    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False
    )
    content = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    author = relationship(
        "User", foreign_keys=[author_id], back_populates="sent_messages"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="receiver_messages"
    )


class Location(Base):
    """
    Location model
    Attributes:
    - id: Integer, primary key
    - city_name: String, unique, not nullable
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), unique=True, nullable=False)

    professionals = relationship("Professional", back_populates="location")
    companies = relationship("Companies", back_populates="location")
    company_offers = relationship("CompanyOffers", back_populates="location")  # NEW
    professional_profiles = relationship(
        "ProfessionalProfile", back_populates="location"
    )