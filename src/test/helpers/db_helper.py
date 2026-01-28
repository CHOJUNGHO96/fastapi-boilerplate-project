"""Database helper utilities for E2E testing."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


async def clear_all_tables(engine: AsyncEngine):
    """
    Clear all data from database tables.

    Args:
        engine: AsyncEngine instance
    """
    async with engine.begin() as conn:
        # Disable foreign key checks temporarily
        await conn.execute(text("SET session_replication_role = 'replica';"))

        # Truncate all tables
        await conn.execute(text("TRUNCATE TABLE users CASCADE;"))

        # Re-enable foreign key checks
        await conn.execute(text("SET session_replication_role = 'origin';"))


async def ensure_clean_database(engine: AsyncEngine):
    """
    Ensure database is clean and ready for testing.
    Creates tables if they don't exist and clears existing data.

    Args:
        engine: AsyncEngine instance
    """
    from infrastructure.db.schema.base import Base

    # Create all tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Clear all existing data
    await clear_all_tables(engine)


async def get_user_from_db(engine: AsyncEngine, login_id: str):
    """
    Retrieve user from database by login_id.

    Args:
        engine: AsyncEngine instance
        login_id: User login_id to search for

    Returns:
        User record or None
    """
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT * FROM users WHERE login_id = :login_id"), {"login_id": login_id})
        return result.first()


async def delete_user_from_db(engine: AsyncEngine, login_id: str):
    """
    Delete user from database by login_id.

    Args:
        engine: AsyncEngine instance
        login_id: User login_id to delete
    """
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users WHERE login_id = :login_id"), {"login_id": login_id})
