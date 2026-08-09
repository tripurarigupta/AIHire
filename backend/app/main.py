from fastapi import FastAPI
from app.api.routes.auth import router as auth_router

app = FastAPI(
    title = "AIHire",
    description = "AI-Powered Recruitment and Interview Preparation Platform",
    version= "1.0.0"
)


app.include_router(auth_router)