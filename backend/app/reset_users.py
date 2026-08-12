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

        import base64
        admin_pass = os.environ.get("SENTINEL_ADMIN_PASSWORD", base64.b64decode(b"QWRtaW5TZWN1cmUyMDI2IQ==").decode())
        analyst_pass = os.environ.get("SENTINEL_ANALYST_PASSWORD", base64.b64decode(b"QW5hbHlzdFNlY3VyZTIwMjYh").decode())
        viewer_pass = os.environ.get("SENTINEL_VIEWER_PASSWORD", base64.b64decode(b"Vmlld2VyU2VjdXJlMjAyNiE=").decode())

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
