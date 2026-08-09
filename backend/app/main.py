from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title = "AIHire",
    description = "AI-Powered Recruitment and Interview Preparation Platform",
    version= "1.0.0"
)
