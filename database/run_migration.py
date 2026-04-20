"""Database migration runner for ML Stroke Guard."""

import os
import sys
from pathlib import Path

import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

load_dotenv()


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}OK {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}ERROR {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}INFO {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}WARN {text}{Colors.ENDC}")


def resolve_connection_string() -> str:
    """Resolve the database connection string from env vars."""
    conn_string = (
        os.getenv("NEON_URL")
        or os.getenv("DATABASE_URL_DIRECT")
        or os.getenv("DATABASE_URL")
    )

    if conn_string:
        return conn_string

    raise ValueError(
        "No database connection string found.\n"
        "Add one of these to .env:\n"
        "  - NEON_URL\n"
        "  - DATABASE_URL_DIRECT\n"
        "  - DATABASE_URL"
    )


def get_db_connection():
    """Create database connection from environment variables."""
    try:
        conn_string = resolve_connection_string()
        destination = conn_string.split("@", 1)[1] if "@" in conn_string else "database"
        print_info(f"Connecting to: {destination}")

        return psycopg2.connect(
            conn_string,
            connect_timeout=10,
        )
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        print_info("Check your Neon project status and connection string in .env.")
        sys.exit(1)


def run_sql_file(cursor, file_path):
    """Execute SQL file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
            cursor.execute(sql_content)
        return True
    except Error as e:
        message = str(e).lower()
        duplicate_markers = (
            "already exists",
            "already a member of extension",
            "duplicate key value",
        )
        if any(marker in message for marker in duplicate_markers):
            cursor.connection.rollback()
            print_warning(f"Skipping {file_path.name}: existing objects detected")
            return True
        print_error(f"Error executing {file_path}: {e}")
        return False
    except Exception as e:
        print_error(f"Error executing {file_path}: {e}")
        return False


def run_migrations(cursor, conn):
    """Run all migration files."""
    print_header("RUNNING MIGRATIONS")

    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print_warning("No migration files found.")
        return False

    success_count = 0
    for migration_file in migration_files:
        print_info(f"Executing: {migration_file.name}")

        if run_sql_file(cursor, migration_file):
            conn.commit()
            print_success(f"Completed: {migration_file.name}")
            success_count += 1
        else:
            conn.rollback()
            print_error(f"Failed: {migration_file.name}")
            return False

    print_success(f"All {success_count} migrations completed successfully.")
    return True


def run_seeds(cursor, conn, include_sample_data=False):
    """Run all seed files."""
    print_header("RUNNING SEEDS")

    seeds_dir = Path(__file__).parent / "seeds"
    seed_files = [seeds_dir / "001_seed_admin_user.sql"]

    if include_sample_data:
        sample_data_file = seeds_dir / "002_seed_sample_data.sql"
        if sample_data_file.exists():
            seed_files.append(sample_data_file)

    success_count = 0
    for seed_file in seed_files:
        if not seed_file.exists():
            print_warning(f"Seed file not found: {seed_file.name}")
            continue

        print_info(f"Executing: {seed_file.name}")

        if run_sql_file(cursor, seed_file):
            conn.commit()
            print_success(f"Completed: {seed_file.name}")
            success_count += 1
        else:
            conn.rollback()
            print_warning(f"Skipped: {seed_file.name} (may already exist)")

    print_success(f"{success_count} seed files executed.")
    return True


def verify_migration(cursor):
    """Verify that tables were created."""
    print_header("VERIFYING MIGRATION")

    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
    )

    tables = cursor.fetchall()

    if tables:
        print_info("Tables created:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print_warning("No tables found.")
        return False

    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
    )

    views = cursor.fetchall()

    if views:
        print_info("Views created:")
        for view in views:
            print(f"  - {view[0]}")

    cursor.execute("SELECT email, role FROM users WHERE role = 'ADMIN' LIMIT 1;")
    admin = cursor.fetchone()

    if admin:
        print_success(f"Admin user created: {admin[0]}")
    else:
        print_warning("No admin user found.")

    return True


def main():
    """Run migrations and seeds against Neon PostgreSQL."""
    print_header("ML STROKE GUARD - DATABASE MIGRATION")

    if not os.path.exists(".env"):
        print_error(".env file not found.")
        print_info("Please create .env file with your Neon database credentials.")
        sys.exit(1)

    print_warning("This will create or modify database tables.")
    response = input(f"{Colors.BOLD}Continue? (y/n): {Colors.ENDC}").lower()

    if response != "y":
        print_info("Migration cancelled.")
        sys.exit(0)

    sample_data = input(
        f"{Colors.BOLD}Include sample data for testing? (y/n): {Colors.ENDC}"
    ).lower() == "y"

    print_info("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    print_success("Connected to database.")

    try:
        if not run_migrations(cursor, conn):
            print_error("Migration failed.")
            sys.exit(1)

        if not run_seeds(cursor, conn, include_sample_data=sample_data):
            print_error("Seeding failed.")
            sys.exit(1)

        verify_migration(cursor)

        print_header("MIGRATION COMPLETED SUCCESSFULLY")
        print_success("Database is ready to use.")

        if not sample_data:
            print_info("Default admin credentials:")
            print("  Email: admin@strokeguard.com")
            print("  Password: Admin123!")
            print_warning("Change this password after the first login.")

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
        print_info("Database connection closed.")


if __name__ == "__main__":
    main()
