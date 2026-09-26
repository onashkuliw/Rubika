import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")
DEFAULT_SCORE = int(os.getenv("DEFAULT_SCORE", "3"))
BOT_NAME = os.getenv("BOT_NAME", "یار رسانه")
GROUP_ID = os.getenv("GROUP_ID", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID is not set")
