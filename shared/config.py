import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT") or 5432
RABBIT_HOST = os.getenv("RABBIT_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
ADMIN_ID = os.getenv("ADMIN_ID")
POSTGRES_TEST_DB = os.getenv("POSTGRES_TEST_DB")

# Bot app
DIGESTS_LIMIT = 7
RETRY_LIMIT = 50
