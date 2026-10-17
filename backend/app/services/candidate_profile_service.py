from sqlalchemy.orm import Session

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
    add_resume_file,
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
    

# Resumes are stored in the database, not on disk. The API is deployed to a
# serverless platform whose filesystem is read-only apart from /tmp, and anything
# written there is discarded with the instance - so a resume saved to disk either
# fails to write or is missing when a recruiter later tries to download it.
#
# Hosting platforms also cap the request body (Vercel Functions reject anything
# over 4.5 MB before the request reaches the app), so this limit fails early with
# a readable message and keeps a margin under that ceiling.
MAX_RESUME_BYTES = 4 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx"}

# Known MIME types per extension; other MIME values fall back to the extension check
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

CONTENT_TYPES_BY_EXTENSION = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _resolve_content_type(file: UploadFile, file_extension: str) -> str:
    """Content type to hand back when this upload is downloaded again."""
    if file.content_type in ALLOWED_CONTENT_TYPES:
        return file.content_type
    return CONTENT_TYPES_BY_EXTENSION.get(file_extension, "application/octet-stream")


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

    # Read the upload once and hold it in memory: the same bytes get parsed and
    # then stored, so nothing in this flow depends on the filesystem.
    file_bytes = file.file.read()

    if not file_bytes:
        raise ValueError("The uploaded file is empty")

    if len(file_bytes) > MAX_RESUME_BYTES:
        raise ValueError(
            f"Resume must be {MAX_RESUME_BYTES // (1024 * 1024)} MB or smaller"
        )

    # Branch the parsing logic based on the file extension
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_bytes)
    else:
        extracted_text = extract_text_from_docx(file_bytes)

    extracted_skills_string = extract_skills_from_text(extracted_text)

    profile.skills = extracted_skills_string
    db.commit()
    db.refresh(profile)

    # Heuristic ATS-style analysis of the parsed resume content
    analysis = analyze_resume(extracted_text, extracted_skills_string)

    resume = add_resume_to_profile(
        db=db,
        candidate_id=profile.id,
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

    # Keep the bytes with the resume so recruiters can download it no matter
    # which serverless instance serves the request.
    add_resume_file(
        db=db,
        resume_id=resume.id,
        file_name=original_file_name,
        data=file_bytes,
        content_type=_resolve_content_type(file, file_extension),
    )

    # Re-read so the response carries the resume that was just stored.
    return get_candidate_profile_by_id(db, profile.id)


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