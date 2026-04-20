"""Database connection and utilities."""

import logging
import os
from contextlib import contextmanager
from typing import Generator
from urllib.parse import parse_qsl, urlparse

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

load_dotenv()

logger = logging.getLogger(__name__)

db_pool = None


def _build_connection_params(database_url: str) -> dict:
    """Convert a PostgreSQL URL into psycopg2 parameters."""
    result = urlparse(database_url)
    query_params = dict(parse_qsl(result.query))

    conn_params = {
        "host": result.hostname,
        "port": result.port or 5432,
        "database": result.path.lstrip("/"),
        "user": result.username,
        "password": result.password,
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }

    sslmode = query_params.get("sslmode")
    if sslmode:
        conn_params["sslmode"] = sslmode

    channel_binding = query_params.get("channel_binding")
    if channel_binding:
        conn_params["channel_binding"] = channel_binding

    return conn_params


def init_db_pool():
    """Initialize the connection pool with Neon-first fallbacks."""
    global db_pool

    database_urls = [
        ("NEON_URL", os.getenv("NEON_URL")),
        ("DATABASE_URL_DIRECT", os.getenv("DATABASE_URL_DIRECT")),
        ("DATABASE_URL", os.getenv("DATABASE_URL")),
    ]

    last_error = None

    for url_name, database_url in database_urls:
        if not database_url:
            continue

        try:
            logger.info(f"Trying to connect using {url_name}...")

            db_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **_build_connection_params(database_url),
            )

            test_conn = db_pool.getconn()
            cursor = test_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            test_conn.close()
            db_pool.putconn(test_conn)

            logger.info(f"Database connection pool initialized successfully using {url_name}")
            return
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to connect using {url_name}: {e}")
            if db_pool:
                try:
                    db_pool.closeall()
                except Exception:
                    pass
                db_pool = None

    logger.error("=" * 60)
    logger.error("FAILED TO CONNECT TO DATABASE")
    logger.error("=" * 60)
    logger.error(f"Last error: {last_error}")
    logger.error("")
    logger.error("Possible solutions:")
    logger.error("1. Check your internet connection")
    logger.error("2. Verify NEON_URL or DATABASE_URL_DIRECT in .env")
    logger.error("3. Ensure your Neon connection string is valid")
    logger.error("4. Check that sslmode=require is included in the URL")
    logger.error("5. Check if firewall is blocking the connection")
    logger.error("=" * 60)
    raise Exception(f"Could not connect to database. Last error: {last_error}")


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections.
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    if db_pool is None:
        init_db_pool()

    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db_pool.putconn(conn)


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor) -> Generator:
    """
    Context manager for database cursor.
    Returns dict-like results by default.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()


def close_db_pool():
    """Close all database connections."""
    global db_pool
    if db_pool:
        db_pool.closeall()
        logger.info("Database connection pool closed")
