from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.notification_service import (
    list_notifications,
    get_notification_count,
    read_notification,
    read_all_notifications,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def _serialize(notification):
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "link": notification.link,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
    }


@router.get("")
def get_my_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = list_notifications(db, current_user.id, limit=limit)
    return [
        _serialize(n)
        for n in items
    ]


@router.get("/unread-count")
def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"count": get_notification_count(db, current_user.id)}


@router.post("/{notification_id}/read")
def mark_one_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return _serialize(read_notification(db, current_user.id, notification_id))
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


@router.post("/read-all")
def mark_all_read_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return read_all_notifications(db, current_user.id)