from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.services.admin_service import (
    get_dashboard_stats,
    list_users,
    toggle_user_active,
    list_recent_jobs,
    list_recent_interviews,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/dashboard-stats")
def get_stats(
    _: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    return get_dashboard_stats(db)


@router.get("/users")
def get_users(
    limit: int = 100,
    offset: int = 0,
    _: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    return list_users(db, limit=limit, offset=offset)


@router.post("/users/{user_id}/toggle-active")
def toggle_active(
    user_id: UUID,
    admin: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    try:
        return toggle_user_active(db, user_id=admin.id, target_user_id=user_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get("/jobs")
def get_jobs(
    limit: int = 20,
    _: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    return list_recent_jobs(db, limit=limit)


@router.get("/interviews")
def get_interviews(
    limit: int = 20,
    _: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    return list_recent_interviews(db, limit=limit)