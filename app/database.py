"""
Database connection and utilities
"""
import os
from contextlib import contextmanager
from typing import Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database connection pool
db_pool = None

def init_db_pool():
    """Initialize database connection pool with fallback"""
    global db_pool
    
    # Try DATABASE_URL_DIRECT first, fallback to DATABASE_URL_SESSION
    database_urls = [
        ('DATABASE_URL_DIRECT', os.getenv('DATABASE_URL_DIRECT')),
        ('DATABASE_URL_SESSION', os.getenv('DATABASE_URL_SESSION')),
        ('DATABASE_URL_TRANSACTION', os.getenv('DATABASE_URL_TRANSACTION')),
    ]
    
    last_error = None
    
    for url_name, database_url in database_urls:
        if not database_url:
            continue
            
        try:
            logger.info(f"Trying to connect using {url_name}...")
            
            # Parse connection string
            import urllib.parse
            result = urllib.parse.urlparse(database_url)
            
            # Build connection parameters
            conn_params = {
                'host': result.hostname,
                'port': result.port or 5432,
                'database': result.path.lstrip('/'),
                'user': result.username,
                'password': result.password,
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
            }
            
            # Create pool
            db_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **conn_params
            )
            
            # Test connection
            test_conn = db_pool.getconn()
            cursor = test_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            test_conn.close()
            db_pool.putconn(test_conn)
            
            logger.info(f"✓ Database connection pool initialized successfully using {url_name}")
            return  # Success!
            
        except Exception as e:
            last_error = e
            logger.warning(f"✗ Failed to connect using {url_name}: {e}")
            if db_pool:
                try:
                    db_pool.closeall()
                except:
                    pass
                db_pool = None
            continue
    
    # If we get here, all connection attempts failed
    logger.error("=" * 60)
    logger.error("FAILED TO CONNECT TO DATABASE")
    logger.error("=" * 60)
    logger.error(f"Last error: {last_error}")
    logger.error("")
    logger.error("Possible solutions:")
    logger.error("1. Check your internet connection")
    logger.error("2. Verify database URLs in .env file")
    logger.error("3. Your network may not support IPv6 (Supabase direct connection)")
    logger.error("4. Try adding DATABASE_URL_SESSION to .env (uses IPv4)")
    logger.error("5. Check if firewall is blocking the connection")
    logger.error("=" * 60)
    raise Exception(f"Could not connect to database. Last error: {last_error}")

@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections
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
    Context manager for database cursor
    Returns dict-like results by default
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()

def close_db_pool():
    """Close all database connections"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        logger.info("Database connection pool closed")
