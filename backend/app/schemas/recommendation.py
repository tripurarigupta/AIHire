from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class RecommendationCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID
    match_percentage: float | None = None
    missing_skills: dict | None = None


class RecommendationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    match_percentage: float | None = None
    missing_skills: dict | None = None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }
