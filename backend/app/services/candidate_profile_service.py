from sqlalchemy.orm import Session

import os
import shutil
import uuid
from fastapi import UploadFile

from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    create_candidate_profile,
    add_resume_to_profile,
)
from app.schemas.candidate_profile import CandidateProfileCreate


def create_profile(
    db: Session,
    user_id,
    data: CandidateProfileCreate,
):
    existing_profile = get_candidate_profile_by_user_id(
        db,
        user_id,
    )

    if existing_profile:
        raise ValueError("Candidate profile already exists")

    return create_candidate_profile(
        db=db,
        user_id=user_id,
        education=data.education,
        experience=data.experience,
        skills=data.skills,
    )
    

# Create the directory if it doesn't exist
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_candidate_resume(
    db: Session,
    user_id: uuid.UUID,
    file: UploadFile,
):
    profile = get_candidate_profile_by_user_id(db, user_id)
    if not profile:
        raise ValueError("Candidate profile must be created first")

    if file.content_type != "application/pdf":
        raise ValueError("Only PDF files are allowed")

    # Keep the same file-saving logic
    file_extension = file.filename.split(".")[-1] if file.filename else "pdf"
    unique_filename = f"{profile.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # NEW: Call the new repository function, passing the original file name
    original_file_name = file.filename or "resume.pdf"
    
    return add_resume_to_profile(
        db=db, 
        candidate_id=profile.id, 
        file_path=file_path, 
        file_name=original_file_name
    )