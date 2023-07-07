import os
import time
import psycopg2
from psycopg2 import OperationalError


def create_conn():
    conn = None
    while not conn:
        try:
            conn = psycopg2.connect(
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            print("Database connection successful")
        except OperationalError:
            print("Database not ready yet. Waiting 5 seconds...")
            time.sleep(5)
    return conn


create_conn()
