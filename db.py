"""
SQLite storage for tracking first-time users.

Keeps a record of Telegram user IDs that have already triggered
the goal event so that we never send the same goal twice.
"""

import aiosqlite

from config import DB_PATH

DB_TIMEOUT_SECONDS = 5


async def init_db() -> None:
    """Create the users table if it does not exist."""
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT_SECONDS) as conn:
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA busy_timeout = 5000")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_users (
                user_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.commit()


async def mark_user_seen(user_id: int) -> bool:
    """Record that the user has started the bot (idempotent).

    Returns True only if this call inserted a new row.
    """
    async with aiosqlite.connect(DB_PATH, timeout=DB_TIMEOUT_SECONDS) as conn:
        await conn.execute("PRAGMA busy_timeout = 5000")
        cursor = await conn.execute(
            "INSERT OR IGNORE INTO seen_users (user_id) VALUES (?)", (user_id,)
        )
        await conn.commit()
        return cursor.rowcount == 1
