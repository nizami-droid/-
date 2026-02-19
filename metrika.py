"""
Yandex.Metrika Measurement Protocol client.

Sends goal (target) events to Yandex.Metrika counter via the
server-side hit API endpoint.

Reference: https://yandex.ru/support/metrica/data/hit-api.html
"""

import logging
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
      - t      : hit type ("event")
      - e      : goal identifier (name of the goal as configured in Metrika)
      - en     : event name (human-readable)
      - url    : page URL
      - title  : page title
      - rn     : random nonce (cache buster)

    Returns True on success, False otherwise.
    """
    url = METRIKA_HIT_URL.format(counter_id=counter_id)
    params = {
        "id": counter_id,
        "wmode": "6",
        "v": "5",
        "t": "event",
        "e": goal_name,
        "en": goal_name,
        "url": page_url,
        "title": page_title,
        "uid": str(user_id),
        "rn": uuid.uuid4().hex,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
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
