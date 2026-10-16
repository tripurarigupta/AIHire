from sqlalchemy.orm import Session

from app.repositories.notification_repository import (
    create_notification,
    get_notifications_for_user,
    get_unread_count,
    get_notification_by_id,
    mark_notification_read,
    mark_all_read,
)



def list_notifications(
    db: Session,
    user_id,
    limit: int = 20,
):
    return get_notifications_for_user(db, user_id, limit=limit)


def get_notification_count(
    db: Session,
    user_id,
):
    return get_unread_count(db, user_id)


def read_notification(
    db: Session,
    user_id,
    notification_id,
):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise ValueError("Notification not found")
    if str(notification.user_id) != str(user_id):
        raise PermissionError("You do not have permission to update this notification")
    return mark_notification_read(db, notification)


def read_all_notifications(
    db: Session,
    user_id,
):
    mark_all_read(db, user_id)
    return {"message": "All notifications marked as read"}