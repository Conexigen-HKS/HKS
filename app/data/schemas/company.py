
from app.data.schemas.user import BaseUser
class Company(BaseUser):
    role: str = "company"
    company_name: str

    @classmethod
    def create_company(cls, username: str, password: str, company_name: str):
        return cls(username=username, password=password, company_name=company_name)

