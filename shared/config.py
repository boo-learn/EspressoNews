import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
RABBIT_HOST = os.getenv("RABBIT_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
ADMIN_ID = os.getenv("ADMIN_ID")
