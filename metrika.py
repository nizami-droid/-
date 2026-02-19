"""
Yandex.Metrika Measurement Protocol client.

Sends goal (target) events to Yandex.Metrika counter via the
server-side hit API endpoint.

Reference: https://yandex.ru/support/metrica/data/hit-api.html
"""

import logging
import time
import uuid

import aiohttp

logger = logging.getLogger(__name__)

METRIKA_HIT_URL = "https://mc.yandex.ru/watch/{counter_id}"


async def send_goal(
    counter_id: str,
    goal_name: str,
    user_id: int,
    *,
    page_url: str = "https://t.me/bot",
    page_title: str = "Telegram Bot",
) -> bool:
    """
    Send a goal hit to Yandex.Metrika.

    The Yandex.Metrika hit API accepts GET requests with the following
    required parameters:
      - wmode  : watch mode (6 = goal event)
      - v      : protocol version
      - t      : hit type ("reachGoal")
      - e      : goal identifier (name of the goal as configured in Metrika)
      - url    : page URL
      - title  : page title
      - rn     : random nonce (cache buster)

    Also sends Cookie header with _ym_uid (Telegram user_id) so Metrika
    can attribute the hit to a visitor instead of discarding it.

    Returns True on success, False otherwise.
    """
    url = METRIKA_HIT_URL.format(counter_id=counter_id)
    params = {
        "id": counter_id,
        "wmode": "6",
        "v": "5",
        "t": "reachGoal",
        "e": goal_name,
        "url": page_url,
        "title": page_title,
        "rn": uuid.uuid4().hex,
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Cookie": f"_ym_uid={user_id}; _ym_d={int(time.time())}",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    logger.info(
                        "Goal '%s' sent to Metrika counter %s for user %s",
                        goal_name,
                        counter_id,
                        user_id,
                    )
                    return True
                else:
                    logger.warning(
                        "Metrika returned HTTP %s for user %s",
                        resp.status,
                        user_id,
                    )
                    return False
    except aiohttp.ClientError as exc:
        logger.error("Failed to send goal to Metrika: %s", exc)
        return False
