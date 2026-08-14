import asyncio
import os
from sqlalchemy import select, delete
from backend.app.database import AsyncSessionFactory, init_db, Base, async_engine
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.models.incident import Incident
from backend.app.models.model_registry import ModelRegistry
from backend.app.security import hash_password, verify_password


async def reset_and_seed_users():
    """Wipes user records and re-seeds fresh admin, analyst, viewer users with verified bcrypt hashes."""
    print("--> Initializing DB schema...")
    await init_db()

    async with AsyncSessionFactory() as db:
        print("--> Clearing existing users...")
        await db.execute(delete(User))
        await db.commit()

        from backend.app.config import settings

        admin_pass = settings.SENTINEL_ADMIN_PASSWORD or os.environ.get("SENTINEL_ADMIN_PASSWORD")
        analyst_pass = settings.SENTINEL_ANALYST_PASSWORD or os.environ.get("SENTINEL_ANALYST_PASSWORD")
        viewer_pass = settings.SENTINEL_VIEWER_PASSWORD or os.environ.get("SENTINEL_VIEWER_PASSWORD")

        if not admin_pass or not analyst_pass or not viewer_pass:
            raise RuntimeError(
                "Security Error: Mandatory environment variables missing!\n"
                "Please set SENTINEL_ADMIN_PASSWORD, SENTINEL_ANALYST_PASSWORD, and SENTINEL_VIEWER_PASSWORD."
            )

        users_data = [
            ("admin", "admin@sentinelai.io", admin_pass, "System Administrator", "admin"),
            ("analyst", "analyst@sentinelai.io", analyst_pass, "Senior Security Analyst", "analyst"),
            ("viewer", "viewer@sentinelai.io", viewer_pass, "Security Operations Viewer", "viewer"),
        ]

        for username, email, raw_password, full_name, role in users_data:
            pwd_hash = hash_password(raw_password)
            is_valid = verify_password(raw_password, pwd_hash)
            print(f"--> Seeding {username} ({role}) - Self-verify: {is_valid}")

            user = User(
                username=username,
                email=email,
                password_hash=pwd_hash,
                full_name=full_name,
                role=role,
                is_active=True
            )
            db.add(user)

        await db.commit()
        print("--> All users successfully reset and verified!")


if __name__ == "__main__":
    asyncio.run(reset_and_seed_users())
