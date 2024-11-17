from company.data.database import Session
from company.models.company_model import CompanyAdBase, CompanyAdModel


def show_all_ads_service(username: str):
    with Session() as session:

        ads = session.query(CompanyAdBase).all()
        return [CompanyAdModel(**ad.__dict__) for ad in ads]