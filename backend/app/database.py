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
    from sqlalchemy.pool import NullPool
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 60.0}
    engine_kwargs["poolclass"] = NullPool
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
AsyncSessionLocal = AsyncSessionFactory


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

        def _safe_migrate(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            table_names = inspector.get_table_names()

            if "model_registry" in table_names:
                mr_cols = {col["name"] for col in inspector.get_columns("model_registry")}
                if "artifact_type" not in mr_cols:
                    sync_conn.execute(text("ALTER TABLE model_registry ADD COLUMN artifact_type VARCHAR(30)"))

            if "incidents" in table_names:
                inc_cols = {col["name"] for col in inspector.get_columns("incidents")}
                inc_migrations = [
                    ("incident_code", "ALTER TABLE incidents ADD COLUMN incident_code VARCHAR(50)"),
                    ("asset_id", "ALTER TABLE incidents ADD COLUMN asset_id VARCHAR(36)"),
                    ("title", "ALTER TABLE incidents ADD COLUMN title VARCHAR(255)"),
                    ("description", "ALTER TABLE incidents ADD COLUMN description TEXT"),
                    ("risk_score", "ALTER TABLE incidents ADD COLUMN risk_score FLOAT DEFAULT 0.0"),
                    ("alert_count", "ALTER TABLE incidents ADD COLUMN alert_count INTEGER DEFAULT 1"),
                    ("first_seen", "ALTER TABLE incidents ADD COLUMN first_seen TIMESTAMP"),
                    ("last_seen", "ALTER TABLE incidents ADD COLUMN last_seen TIMESTAMP"),
                    ("resolution", "ALTER TABLE incidents ADD COLUMN resolution TEXT")
                ]
                for col_name, sql in inc_migrations:
                    if col_name not in inc_cols:
                        sync_conn.execute(text(sql))

            if "alerts" in table_names:
                alt_cols = {col["name"] for col in inspector.get_columns("alerts")}
                alt_migrations = [
                    ("packet_length", "ALTER TABLE alerts ADD COLUMN packet_length INTEGER DEFAULT 0"),
                    ("flow_duration", "ALTER TABLE alerts ADD COLUMN flow_duration FLOAT DEFAULT 0.0")
                ]
                for col_name, sql in alt_migrations:
                    if col_name not in alt_cols:
                        sync_conn.execute(text(sql))

            if "playbook_executions" in table_names:
                pb_cols = {col["name"] for col in inspector.get_columns("playbook_executions")}
                pb_migrations = [
                    ("audit_id", "ALTER TABLE playbook_executions ADD COLUMN audit_id VARCHAR(36)"),
                    ("actor_role", "ALTER TABLE playbook_executions ADD COLUMN actor_role VARCHAR(30) DEFAULT 'analyst'"),
                    ("authorization_decision", "ALTER TABLE playbook_executions ADD COLUMN authorization_decision VARCHAR(30) DEFAULT 'APPROVED'")
                ]
                for col_name, sql in pb_migrations:
                    if col_name not in pb_cols:
                        sync_conn.execute(text(sql))

            # Performance & Scalability Composite Indexes (Phase 2 & Phase 4)
            index_statements = [
                "CREATE INDEX IF NOT EXISTS idx_alerts_src_dst_ts ON alerts (source_ip, destination_ip, timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_incidents_status_lastseen ON incidents (status, last_seen)",
                "CREATE INDEX IF NOT EXISTS idx_sec_events_type_ts ON security_events (event_type, timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_org_slug ON organizations (slug)",
                "CREATE INDEX IF NOT EXISTS idx_tenant_org ON tenants (organization_id)",
                "CREATE INDEX IF NOT EXISTS idx_membership_user_org ON tenant_memberships (user_id, organization_id)",
                "CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys (key_prefix)",
                "CREATE INDEX IF NOT EXISTS idx_usage_tenant_ts ON usage_records (tenant_id, timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_sensors_tenant ON sensors (tenant_id)"
            ]
            for idx_sql in index_statements:
                try:
                    sync_conn.execute(text(idx_sql))
                except Exception as idx_err:
                    logger.debug("Index creation skipped: %s", idx_err)

        await conn.run_sync(_safe_migrate)
        logger.info("Database tables successfully initialized.")

