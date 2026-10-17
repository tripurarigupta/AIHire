from uuid import UUID
from pydantic import BaseModel


class CandidateProfileCreate(BaseModel):
    phone: str | None = None
    address: str | None = None
    headline: str | None = None
    bio: str | None = None
    education: str | None = None
    experience: str | None = None
    skills: str | None = None


class ResumeResponse(BaseModel):
    id: UUID
    file_name: str
    # Only set for resumes uploaded before the bytes moved into the database.
    file_path: str | None = None
    ats_score: float | None = None
    parsed_skills: dict | None = None

    model_config = {
        "from_attributes": True,
    }


class ResumeAnalysisResponse(BaseModel):
    resume_id: UUID
    file_name: str
    ats_score: float | None = None
    word_count: int | None = None
    skills_detected: list[str] = []
    suggestions: list[str] = []
    strengths: list[str] = []


class CandidateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    phone: str | None = None
    address: str | None = None
    headline: str | None = None
    bio: str | None = None
    education: str | None = None
    experience: str | None = None
    skills: str | None = None
    resumes: list[ResumeResponse] = []

    model_config = {
        "from_attributes": True,
    }