from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, event, Float

Base = declarative_base()


class ProfesionalBase(Base):
    __tablename__ = "profesionals"
    profesional_id = Column(Integer, primary_key=True)