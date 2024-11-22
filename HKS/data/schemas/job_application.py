from uuid import UUID

from pydantic import BaseModel, UUID4, Field, root_validator, field_validator, model_validator
from typing import Optional, List

from pydantic import BaseModel, UUID4, ValidationError

class CompanyOfferCreate(BaseModel):
    company_id: Optional[UUID]
    professional_profile_id: Optional[UUID]
    offer_type: str
    status: str
    min_salary: int
    max_salary: int
    location: Optional[str]
    description: Optional[str]

    @model_validator(mode="after")
    def validate_offer_type(self):
        # Conditional validation based on offer_type
        if self.offer_type == "company":
            if not self.company_id:
                raise ValueError("company_id is required for company offers")
            # Ensure professional_profile_id is not mistakenly required for company offers
            if self.professional_profile_id is not None:
                raise ValueError("professional_profile_id should not be provided for company offers")
        elif self.offer_type == "professional":
            if not self.professional_profile_id:
                raise ValueError("professional_profile_id is required for professional applications")
            # Ensure company_id is not mistakenly required for professional offers
            if self.company_id is not None:
                raise ValueError("company_id should not be provided for professional applications")
        else:
            raise ValueError("Invalid offer_type. It must be either 'company' or 'professional'.")
        return self

class CompanyOfferResponse(BaseModel):
    id: UUID
    company_id: UUID
    min_salary: Optional[int]
    max_salary: Optional[int]
    status: str

    class Config:
        orm_mode = True