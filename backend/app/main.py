from fastapi import FastAPI
from app.core.config import settings
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


# Origins the browser app is served from. Add a custom domain through the
# CORS_EXTRA_ORIGINS environment variable instead of editing this list, so a new
# domain does not need a code change and a redeploy of the API.
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://aihire-three.vercel.app",
]

ALLOWED_ORIGINS = DEFAULT_ALLOWED_ORIGINS + [
    origin.strip().rstrip("/")
    for origin in settings.CORS_EXTRA_ORIGINS.split(",")
    if origin.strip()
]

# Every Vercel preview deployment gets its own hostname
# (e.g. aihire-three-git-main-team.vercel.app), so they cannot be listed one by
# one. Scoped to this project's name rather than all of *.vercel.app so that an
# unrelated Vercel site cannot call the API with the browser's credentials.
ALLOWED_ORIGIN_REGEX = r"https://aihire-three[a-z0-9-]*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # The exact Vite frontend URLs
    allow_origin_regex=ALLOWED_ORIGIN_REGEX, # Vercel preview deployments
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