from fastapi import APIRouter, Response, HTTPException, Query
from starlette import status
# from models.job_ad_model import JobAdBase
from app.services.company_service import create_new_company, company_login_service, edit_company_description_service
from app.cummon.auth import create_access_token, decode_access_token
from app.models.company_model import CompanyRegistrationModel, CompanyLoginModel, CompanyInfoModel

company_router = APIRouter(prefix="/companies", tags=["Companies"])


@company_router.post('/register')
def company_registration(company: CompanyRegistrationModel):
    new_company = create_new_company(company.username, company.password, company.company_name)
    token = create_access_token({'username': company.username, 'company_name': company.company_name})

    return {"message": "Company registered successfully", "company": new_company}


@company_router.post('/login')
def company_login(company: CompanyLoginModel, response: Response):
    company_data = company_login_service(company)

    if company_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    token = create_access_token({"username": company.company_username})

    response.headers["Authorization"] = f"Bearer {token}"

    return {"message": f"{company.company_username} Logged in Successfully"}

@company_router.put('/companies/info')
def edit_company_description(company_info: CompanyInfoModel, token: str = Query(..., alias="token")):

    try:
        payload = decode_access_token(token)
        company_username = payload.get("username")

        if company_username is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    updated_company = edit_company_description_service(company_info, company_username)

    if updated_company:
        return {"message": "Company description updated successfully", "company": updated_company}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while updating the company description"
        )


# @company_router.post("/companies/create/job_ad")
# def create_new_job_ad(job_ad: JobAdBase):
#     created_job_ad = create_new_job_ad(job_ad)
#
#     if created_job_ad:
#         return {"message": "Job ad created successfully", "job_ad": created_job_ad}
#     else:
#         raise HTTPException(
#             status_code=400,
#             detail="Error occurred while creating the job ad"
#         )
