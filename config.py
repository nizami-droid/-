import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
METRIKA_COUNTER_ID: str = os.environ["METRIKA_COUNTER_ID"]
METRIKA_GOAL_NAME: str = os.getenv("METRIKA_GOAL_NAME", "bot_start")
DB_PATH: str = os.getenv("DB_PATH", "users.db")
