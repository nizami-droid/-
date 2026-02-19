"""
Telegram bot that sends a Yandex.Metrika goal on first user launch.

Flow:
  1. User sends /start for the first time.
  2. Bot checks SQLite — user is new.
  3. Bot records user as seen (idempotent INSERT OR IGNORE).
  4. Bot fires the goal to Yandex.Metrika via Measurement Protocol.
  5. Bot replies to the user.

Repeated /start commands are silently ignored for metric purposes
(the user still gets a welcome message).
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import config
from db import init_db, is_new_user, mark_user_seen
from metrika import send_goal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    user_id = message.from_user.id

    if await is_new_user(user_id):
        # Mark first so that even if Metrika call fails we don't double-count
        # if the user spams /start very quickly.
        await mark_user_seen(user_id)

        success = await send_goal(
            counter_id=config.METRIKA_COUNTER_ID,
            goal_name=config.METRIKA_GOAL_NAME,
            user_id=user_id,
        )

        if success:
            logger.info("Goal sent for new user %s", user_id)
        else:
            logger.warning("Goal sending failed for new user %s", user_id)

    await message.answer(
        "Добро пожаловать! Я готов к работе."
    )


async def main() -> None:
    await init_db()

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot started. Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
