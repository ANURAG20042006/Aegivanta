from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from backend.app.config import settings
from backend.app.core.logging import logger


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""
    pass


# Determine async engine args based on database driver
engine_kwargs = {}
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True
    })

# Create Async Engine
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    **engine_kwargs
)

# Async Session Factory
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing asynchronous database sessions to API routes."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise e
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes database schema tables and safely executes non-destructive column migrations."""
    import backend.app.models  # Ensure all ORM models are registered with Base.metadata
    async with async_engine.begin() as conn:
        logger.info("Initializing database tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        # Non-destructive migrations for existing sqlite / postgres schemas
        from sqlalchemy import text
        migration_statements = [
            "ALTER TABLE model_registry ADD COLUMN artifact_type VARCHAR(30)",
            "ALTER TABLE incidents ADD COLUMN incident_code VARCHAR(50)",
            "ALTER TABLE incidents ADD COLUMN asset_id VARCHAR(36)",
            "ALTER TABLE incidents ADD COLUMN title VARCHAR(255)",
            "ALTER TABLE incidents ADD COLUMN description TEXT",
            "ALTER TABLE incidents ADD COLUMN risk_score FLOAT DEFAULT 0.0",
            "ALTER TABLE incidents ADD COLUMN alert_count INTEGER DEFAULT 1",
            "ALTER TABLE incidents ADD COLUMN first_seen TIMESTAMP",
            "ALTER TABLE incidents ADD COLUMN last_seen TIMESTAMP",
            "ALTER TABLE incidents ADD COLUMN resolution TEXT"
        ]
        for stmt in migration_statements:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass  # Column already exists or table freshly created
                
        logger.info("Database tables successfully initialized.")
