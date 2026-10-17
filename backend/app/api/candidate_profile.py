from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from urllib.parse import quote
from uuid import UUID
import os

from app.core.security import require_role, get_current_user
from app.models.user import User
from app.models.user_role import UserRole
from app.database.session import get_db
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    ResumeAnalysisResponse,
)
from app.services.candidate_profile_service import create_profile, upload_candidate_resume, get_resume_access
from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    get_resume_file,
)
from app.services.recommendation_service import get_recommendations_for_user


router = APIRouter(
    prefix="/candidate-profile",
    tags=["Candidate Profile"],
)


def _attachment_header(file_name: str | None) -> str:
    """Build a Content-Disposition value that cannot break out of the header.

    Resumes often have non-ASCII names, so the RFC 5987 `filename*` form carries
    the real name while the plain `filename` stays ASCII as a fallback.
    """
    name = (file_name or "resume")
    name = name.replace('"', "").replace("\r", "").replace("\n", "").strip() or "resume"
    ascii_name = name.encode("ascii", "ignore").decode().strip() or "resume"
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(name)}"


@router.get(
    "/me",
    response_model=CandidateProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please upload a resume.",
        )
    return profile


@router.get(
    "/recommendations",
)
def get_recommendations(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    return get_recommendations_for_user(db=db, user_id=current_user.id)


@router.post(
    "",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate_profile(
    data: CandidateProfileCreate,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return create_profile(
            db=db,
            user_id=current_user.id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
        

@router.post(
    "/resume",
    response_model=CandidateProfileResponse,
)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return upload_candidate_resume(
            db=db,
            user_id=current_user.id,
            file=file,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/resume/{resume_id}/analysis",
    response_model=ResumeAnalysisResponse,
)
def get_resume_analysis(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        resume = get_resume_access(
            db=db,
            user=current_user,
            resume_id=resume_id,
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    parsed = resume.parsed_skills or {}
    analysis = parsed.get("analysis") or {}
    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "ats_score": resume.ats_score,
        "word_count": analysis.get("word_count"),
        "skills_detected": parsed.get("skills", []),
        "suggestions": analysis.get("suggestions", []),
        "strengths": analysis.get("strengths", []),
    }


@router.get(
    "/resume/{resume_id}",
)
def download_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        resume = get_resume_access(
            db=db,
            user=current_user,
            resume_id=resume_id,
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    # Uploads are stored in the database, which is the only place that works on
    # a read-only serverless filesystem. Rows created before that change have no
    # stored bytes, so fall back to the file on disk while it is still there.
    stored_file = get_resume_file(db, resume.id)
    if stored_file is not None:
        return Response(
            content=stored_file.data,
            media_type=stored_file.content_type or "application/octet-stream",
            headers={"Content-Disposition": _attachment_header(stored_file.file_name)},
        )

    if resume.file_path and os.path.exists(resume.file_path):
        return FileResponse(
            resume.file_path,
            filename=resume.file_name,
            media_type="application/octet-stream",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resume file not found on server",
    )
        
        
@router.put(
    "/me",
    response_model=CandidateProfileResponse,
)
def update_my_profile(
    data: CandidateProfileCreate,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        return create_profile(db=db, user_id=current_user.id, data=data)

    # Update only provided fields to avoid wiping existing data
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile