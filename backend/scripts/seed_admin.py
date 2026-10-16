"""Create the platform admin user (idempotent) or reset its password.

The public /auth/register endpoint deliberately blocks the admin role, so the
admin account is provisioned here instead. Run from the backend directory:

Create admin (skips if it already exists):
    venv\Scripts\python.exe scripts\seed_admin.py

Reset the existing admin password:
    venv\Scripts\python.exe scripts\seed_admin.py --reset-password "NewPass123!"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User
from app.models.user_role import UserRole

DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@aihire.dev")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123!")


def main() -> None:
    parser = argparse.ArgumentParser(description="AIHire admin provisioning")
    parser.add_argument(
        "--reset-password",
        type=str,
        default=None,
        help="New password for the existing admin account (email via ADMIN_EMAIL or admin@aihire.dev).",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        existing = db.execute(
            select(User).where(User.email == DEFAULT_ADMIN_EMAIL)
        ).scalar_one_or_none()

        if args.reset_password:
            if not existing:
                print(f"No admin found with email {DEFAULT_ADMIN_EMAIL}. Nothing to reset.")
                return

            existing.password_hash = hash_password(args.reset_password)
            db.commit()
            db.refresh(existing)
            print(f"Password updated for {existing.email} (id={existing.id})")
            return

        if existing:
            print(f"Admin already exists: {existing.email} (id={existing.id})")
            print("Use --reset-password to change its password.")
            return

        admin = User(
            full_name="Platform Admin",
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin created: {admin.email} (id={admin.id})")
        print(f"Email:    {DEFAULT_ADMIN_EMAIL}")
        print(f"Password: {DEFAULT_ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()