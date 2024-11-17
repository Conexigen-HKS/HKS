# from sqlalchemy.ext.declarative import declarative_base
# from pydantic import BaseModel
# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, event, Float, Enum
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import insert
# from sqlalchemy import Table, MetaData
# import datetime
# Base = declarative_base()
# class JobAdBase(Base):
#     __tablename__ = 'company_job_ad'
#     job_ad_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
#     position_title = Column(String)
#     salary = Column(Float)
#     job_description = Column(String)
#     ad_created_at = Column(DateTime, default=datetime.datetime.now)
#
#     # Here we store the company name from the CompanyInfoBase
#     company_name = Column(String, ForeignKey('company_info.company_name'))
#     job_location = Column(String)
#
#     # Establish the relationship to the CompanyInfoBase
#     company_info = relationship("CompanyInfoBase", backref="job_ads")