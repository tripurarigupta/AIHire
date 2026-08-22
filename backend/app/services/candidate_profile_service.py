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

from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.docx_parser import extract_text_from_docx
from app.utils.skill_extractor import extract_skills_from_text


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

    # 1. Update Validation to allow both PDF and DOCX
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" # Standard DOCX MIME type
    ]
    if file.content_type not in allowed_types:
        raise ValueError("Only PDF and DOCX files are allowed")

    # Keep file saving logic
    file_extension = file.filename.split(".")[-1].lower() if file.filename else "pdf"
    unique_filename = f"{profile.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Branch the parsing logic based on the file extension
    extracted_text = ""
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(file_path)

    extracted_skills_string = extract_skills_from_text(extracted_text)
    
    profile.skills = extracted_skills_string 
    db.commit()
    db.refresh(profile)
    original_file_name = file.filename or f"resume.{file_extension}"
    
    return add_resume_to_profile(
        db=db, 
        candidate_id=profile.id, 
        file_path=file_path, 
        file_name=original_file_name,
        parsed_text=extracted_text, 
    )