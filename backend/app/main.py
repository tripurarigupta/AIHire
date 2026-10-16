from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.candidate_profile import router as candidate_profile_router
from app.api.recruiter_profile import router as recruiter_profile_router
from app.api.job import router as job_router
from app.api.application import router as application_router
from app.api.interview import router as interview_router
from app.api.notification import router as notification_router
from app.api.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title = "AIHire",
    description = "AI-Powered Recruitment and Interview Preparation Platform",
    version= "1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://aihire-three.vercel.app/"], # The exact Vite frontend URLs
    allow_credentials=True, # Allows the frontend to send cookies or Authorization headers
    allow_methods=["*"], # Allows all HTTP methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"], # Allows all headers
)


app.include_router(auth_router)
app.include_router(candidate_profile_router)
app.include_router(recruiter_profile_router)
app.include_router(job_router)
app.include_router(application_router)
app.include_router(interview_router)
app.include_router(notification_router)
app.include_router(admin_router)