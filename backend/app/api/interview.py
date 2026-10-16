from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.core.security import require_role, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.interview_session import (
    MockInterviewRequest,
    InterviewQuestionSetResponse,
    MockInterviewEvaluationRequest,
    MockInterviewEvaluationResponse,
)
from app.services.interview_service import (
    generate_questions,
    submit_evaluation,
    get_interview_history,
    get_interview_details,
)

router = APIRouter(
    prefix="/interviews",
    tags=["AI Mock Interviews"],
)


@router.post(
    "/questions",
    response_model=InterviewQuestionSetResponse,
)
def generate_questions_endpoint(
    data: MockInterviewRequest,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return generate_questions(
            db=db,
            user_id=current_user.id,
            job_id=data.job_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/evaluate",
    response_model=MockInterviewEvaluationResponse,
)
def evaluate_interview_endpoint(
    data: MockInterviewEvaluationRequest,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return submit_evaluation(
            db=db,
            user_id=current_user.id,
            data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/history",
)
def list_interview_history(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    return get_interview_history(db=db, user_id=current_user.id)


@router.get(
    "/{interview_id}",
)
def get_interview_details_endpoint(
    interview_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_interview_details(
            db=db,
            user=current_user,
            interview_id=interview_id,
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