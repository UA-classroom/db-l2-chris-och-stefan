import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user=os.getenv("DB_USER", "postgres"),
        password=PASSWORD,
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def create_tables(sql_file: str = "sqlwinserts.sql"):
    
    sql_path = Path(__file__).parent / sql_file
    if not sql_path.exists():
        raise FileNotFoundError(f"Could not find SQL file: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    
    create_tables()
    print("Tables created successfully.")
