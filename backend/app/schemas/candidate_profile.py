from uuid import UUID
from pydantic import BaseModel

class CandidateProfileCreate(BaseModel):
    education: str | None = None
    experience: str | None = None
    skills: str | None = None
    
        
class ResumeResponse(BaseModel):
    id: UUID
    file_name: str
    file_path: str

    model_config = {
        "from_attributes": True,
    }
    

class CandidateProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    education: str | None
    experience: str | None
    skills: str | None
    resumes: list[ResumeResponse] = []  

    model_config = {
        "from_attributes": True,
    }