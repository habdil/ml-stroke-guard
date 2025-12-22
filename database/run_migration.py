"""
Database Migration Runner for ML Stroke Guard
Run all migrations and seeds in order
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def get_db_connection():
    """Create database connection from environment variables"""
    try:
        # Try different Supabase connection string formats
        # Priority: DATABASE_URL_DIRECT > DATABASE_URL > individual variables
        
        conn_string = None
        
        # Option 1: DATABASE_URL_DIRECT (recommended for migrations)
        conn_string = os.getenv('DATABASE_URL_DIRECT')
        
        # Option 2: DATABASE_URL (fallback)
        if not conn_string:
            conn_string = os.getenv('DATABASE_URL')
        
        # Option 3: Build from individual variables
        if not conn_string:
            host = os.getenv('SUPABASE_HOST', 'db.supabase.co')
            database = os.getenv('SUPABASE_DB', 'postgres')
            user = os.getenv('SUPABASE_USER', 'postgres')
            password = os.getenv('SUPABASE_PASSWORD')
            port = os.getenv('SUPABASE_PORT', '5432')
            
            if not password:
                raise ValueError(
                    "No database connection string found!\n"
                    "Please add one of these to your .env:\n"
                    "  - DATABASE_URL_DIRECT (recommended)\n"
                    "  - DATABASE_URL\n"
                    "  - Or individual SUPABASE_* variables"
                )
            
            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        print_info(f"Connecting to: {conn_string.split('@')[1] if '@' in conn_string else 'database'}")
        
        # Try to connect with extended timeout and options
        try:
            conn = psycopg2.connect(
                conn_string,
                connect_timeout=10,
                options='-c statement_timeout=30000'
            )
            return conn
        except psycopg2.OperationalError as e:
            # If connection fails, try alternative approaches
            if "could not translate host name" in str(e):
                print_warning("DNS resolution failed. Trying alternative connection method...")
                
                # Try to use Google DNS or Cloudflare DNS
                print_info("Tip: You may need to:")
                print_info("  1. Check your internet connection")
                print_info("  2. Try using VPN if Supabase is blocked")
                print_info("  3. Use Supabase Dashboard SQL Editor instead")
                print_info("  4. Check if your firewall is blocking the connection")
            raise e
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)

def run_sql_file(cursor, file_path):
    """Execute SQL file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            cursor.execute(sql_content)
        return True
    except Exception as e:
        print_error(f"Error executing {file_path}: {e}")
        return False

def run_migrations(cursor, conn):
    """Run all migration files"""
    print_header("RUNNING MIGRATIONS")
    
    migrations_dir = Path(__file__).parent / 'migrations'
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        print_warning("No migration files found!")
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
    
    print_success(f"\nAll {success_count} migrations completed successfully!")
    return True

def run_seeds(cursor, conn, include_sample_data=False):
    """Run all seed files"""
    print_header("RUNNING SEEDS")
    
    seeds_dir = Path(__file__).parent / 'seeds'
    
    # Always run admin seed
    seed_files = [seeds_dir / '001_seed_admin_user.sql']
    
    # Optionally include sample data
    if include_sample_data:
        sample_data_file = seeds_dir / '002_seed_sample_data.sql'
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
    
    print_success(f"\n{success_count} seed files executed!")
    return True

def verify_migration(cursor):
    """Verify that tables were created"""
    print_header("VERIFYING MIGRATION")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print_info("Tables created:")
        for table in tables:
            print(f"  • {table[0]}")
    else:
        print_warning("No tables found!")
        return False
    
    # Check views
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    views = cursor.fetchall()
    
    if views:
        print_info("\nViews created:")
        for view in views:
            print(f"  • {view[0]}")
    
    # Check admin user
    cursor.execute("SELECT email, role FROM users WHERE role = 'ADMIN' LIMIT 1;")
    admin = cursor.fetchone()
    
    if admin:
        print_success(f"\nAdmin user created: {admin[0]}")
    else:
        print_warning("\nNo admin user found!")
    
    return True

def main():
    """Main migration runner"""
    print_header("ML STROKE GUARD - DATABASE MIGRATION")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print_info("Please create .env file with database credentials")
        sys.exit(1)
    
    # Ask for confirmation
    print_warning("This will create/modify database tables.")
    response = input(f"{Colors.BOLD}Continue? (y/n): {Colors.ENDC}").lower()
    
    if response != 'y':
        print_info("Migration cancelled.")
        sys.exit(0)
    
    # Ask about sample data
    sample_data = input(f"{Colors.BOLD}Include sample data for testing? (y/n): {Colors.ENDC}").lower() == 'y'
    
    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    print_success("Connected to database!")
    
    try:
        # Run migrations
        if not run_migrations(cursor, conn):
            print_error("Migration failed!")
            sys.exit(1)
        
        # Run seeds
        if not run_seeds(cursor, conn, include_sample_data=sample_data):
            print_error("Seeding failed!")
            sys.exit(1)
        
        # Verify
        verify_migration(cursor)
        
        print_header("MIGRATION COMPLETED SUCCESSFULLY")
        print_success("Database is ready to use!")
        
        if not sample_data:
            print_info("\nDefault admin credentials:")
            print(f"  Email: admin@strokeguard.com")
            print(f"  Password: Admin123!")
            print_warning("  ⚠ Please change this password after first login!")
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
        print_info("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
