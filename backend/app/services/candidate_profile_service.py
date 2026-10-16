from sqlalchemy.orm import Session

import os
import shutil
import uuid
from fastapi import UploadFile

from app.models.user import User
from app.models.resume import Resume
from app.models.user_role import UserRole
from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    get_candidate_profile_by_id,
    create_candidate_profile,
    add_resume_to_profile,
    get_resume_by_id,
)
from app.repositories.application_repository import has_application_between_candidate_and_recruiter
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
from app.schemas.candidate_profile import CandidateProfileCreate

from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.docx_parser import extract_text_from_docx
from app.utils.skill_extractor import extract_skills_from_text
from app.utils.resume_analyzer import analyze_resume


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
        phone=data.phone,
        address=data.address,
        headline=data.headline,
        bio=data.bio,
        education=data.education,
        experience=data.experience,
        skills=data.skills,
    )
    

# Create the directory if it doesn't exist
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx"}

# Known MIME types per extension; other MIME values fall back to the extension check
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def upload_candidate_resume(
    db: Session,
    user_id: uuid.UUID,
    file: UploadFile,
):
    # Auto-create a minimal profile the first time a candidate uploads a resume,
    # instead of requiring the profile to be manually created first.
    profile = get_candidate_profile_by_user_id(db, user_id)
    if not profile:
        profile = create_candidate_profile(db=db, user_id=user_id)

    # Validate by file extension (primary) and MIME type (when a recognized type is sent).
    # Some browsers/clients send generic types like application/octet-stream, so the
    # extension check is the source of truth.
    original_file_name = file.filename or ""
    file_extension = original_file_name.rsplit(".", 1)[-1].lower() if "." in original_file_name else ""

    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX files are allowed")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        # A recognized-but-unexpected MIME type is a strong signal of a bad upload;
        # unknown/generic types fall back to the extension validation above.
        if file.content_type not in (
            "application/octet-stream",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "binary/octet-stream",
        ):
            raise ValueError("File content does not match a supported format")

    unique_filename = f"{profile.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Branch the parsing logic based on the file extension
    extracted_text = ""
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(file_path)

    extracted_skills_string = extract_skills_from_text(extracted_text)

    profile.skills = extracted_skills_string
    db.commit()
    db.refresh(profile)

    # Heuristic ATS-style analysis of the parsed resume content
    analysis = analyze_resume(extracted_text, extracted_skills_string)

    return add_resume_to_profile(
        db=db,
        candidate_id=profile.id,
        file_path=file_path,
        file_name=original_file_name,
        parsed_text=extracted_text,
        parsed_skills={
            "skills": analysis["skills_detected"],
            "analysis": {
                "ats_score": analysis["ats_score"],
                "word_count": analysis["word_count"],
                "suggestions": analysis["suggestions"],
                "strengths": analysis["strengths"],
            },
        },
        ats_score=analysis["ats_score"],
    )


def get_resume_access(
    db: Session,
    user: User,
    resume_id: uuid.UUID,
) -> Resume:
    """Returns a resume only if the requesting user is allowed to view it."""
    resume = get_resume_by_id(db, resume_id)
    if not resume:
        raise ValueError("Resume not found")

    profile = get_candidate_profile_by_id(db, resume.candidate_id)
    if not profile:
        raise ValueError("Resume not found")

    if user.role == UserRole.CANDIDATE:
        if profile.user_id != user.id:
            raise PermissionError("You do not have permission to access this resume")
        return resume

    if user.role == UserRole.RECRUITER:
        recruiter_profile = get_recruiter_profile_by_user_id(db, user.id)
        if recruiter_profile and has_application_between_candidate_and_recruiter(
            db,
            candidate_id=resume.candidate_id,
            recruiter_id=recruiter_profile.id,
        ):
            return resume

    raise PermissionError("You do not have permission to access this resume")