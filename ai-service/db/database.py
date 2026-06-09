import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "finance_dev")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)


def query(sql: str, params: dict = None) -> list[dict]:
    """
    Execute a raw SELECT and return list of dicts.
    Every tool uses this function.
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def query_one(sql: str, params: dict = None) -> dict | None:
    """Return a single row or None."""
    results = query(sql, params)
    return results[0] if results else None


def test_connection() -> bool:
    """Test DB connection — called on startup."""
    try:
        result = query("SELECT 1 AS ok")
        return result[0]["ok"] == 1
    except Exception as e:
        print(f"DB connection failed: {e}")
        return False