"""
SQLite storage for tracking first-time users.

Keeps a record of Telegram user IDs that have already triggered
the goal event so that we never send the same goal twice.
"""

import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    """Create the users table if it does not exist."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_users (
                user_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.commit()


async def is_new_user(user_id: int) -> bool:
    """Return True if the user has never started the bot before."""
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM seen_users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row is None


async def mark_user_seen(user_id: int) -> None:
    """Record that the user has started the bot (idempotent)."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO seen_users (user_id) VALUES (?)", (user_id,)
        )
        await conn.commit()
