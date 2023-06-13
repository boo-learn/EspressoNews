import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = str(os.getenv("TELEGRAM_BOT_TOKEN"))

OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))

admins = [
    714582939,
    # 335709217
]
