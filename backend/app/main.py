from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.candidate_profile import router as candidate_profile_router
from app.api.recruiter_profile import router as recruiter_profile_router

app = FastAPI(
    title = "AIHire",
    description = "AI-Powered Recruitment and Interview Preparation Platform",
    version= "1.0.0"
)


app.include_router(auth_router)
app.include_router(candidate_profile_router)
app.include_router(recruiter_profile_router)