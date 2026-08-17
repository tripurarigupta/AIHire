from uuid import UUID
from pydantic import BaseModel

class CandidateProfileCreate(BaseModel):
    education: str | None = None
    experience: str | None = None
    skills: str | None = None

class CandidateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    education: str | None
    experience: str | None
    skills: str | None