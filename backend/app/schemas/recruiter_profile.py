from uuid import UUID
from pydantic import BaseModel

class RecruiterProfileCreate(BaseModel):
    company_name: str
    designation: str | None = None
    company_description: str | None = None


class RecruiterProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    designation: str | None
    company_description: str | None