# import sqlalchemy
#
# from models.company_model import CompanyInfoBase
# from models.job_ad_model import JobAdBase
#
#
# def create_job_ad(company_name: str, position_title: str, salary: float, job_description: str):
#     with sqlalchemy.orm.Session() as db:
#         company_info = db.query(CompanyInfoBase).filter_by(company_name=company_name).first()
#
#         if not company_info:
#             raise ValueError(f"No company with name {company_name} found.")
#
#         job_ad = JobAdBase(
#             position_title=position_title,
#             salary=salary,
#             job_description=job_description,
#             job_location=company_info.company_address,
#             company_name=company_name,
#
#         )
#
#         db.add(job_ad)
#         db.commit()
