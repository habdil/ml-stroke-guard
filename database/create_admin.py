"""
Create Admin User Script
Run this to create a new admin user directly in the database
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.auth import get_password_hash
from app.database import get_db_cursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_admin_user(email, password, full_name):
    """
    Create a new admin user in the database
    """
    try:
        # Hash the password
        hashed_password = get_password_hash(password)
        
        print("=" * 60)
        print("CREATING ADMIN USER")
        print("=" * 60)
        print(f"\nEmail: {email}")
        print(f"Password: {password}")
        print(f"Full Name: {full_name}")
        print("\nHashing password...")
        
        # Insert into database
        with get_db_cursor() as cursor:
            # Check if user already exists
            cursor.execute(
                "SELECT id, email FROM users WHERE email = %s",
                (email,)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                print(f"\n⚠️  User with email '{email}' already exists!")
                print(f"User ID: {existing_user['id']}")
                
                # Ask if want to update password
                response = input("\nDo you want to update the password? (y/n): ").lower()
                if response == 'y':
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (hashed_password, email)
                    )
                    print(f"\n✅ Password updated successfully for {email}!")
                else:
                    print("\n❌ Operation cancelled.")
                return
            
            # Insert new admin user
            cursor.execute(
                """
                INSERT INTO users (
                    email, password, full_name, date_of_birth, 
                    gender, phone_number, role
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'ADMIN')
                RETURNING id, email, full_name, role, created_at
                """,
                (
                    email,
                    hashed_password,
                    full_name,
                    date(1990, 1, 1),  # Default date of birth for admin
                    'Male',             # Default gender
                    None                # No phone number
                )
            )
            
            new_user = cursor.fetchone()
            
            print("\n" + "=" * 60)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nUser ID: {new_user['id']}")
            print(f"Email: {new_user['email']}")
            print(f"Full Name: {new_user['full_name']}")
            print(f"Role: {new_user['role']}")
            print(f"Created At: {new_user['created_at']}")
            print("\n" + "=" * 60)
            print("\n🎉 You can now login with these credentials!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ADMIN USER CREATION TOOL")
    print("=" * 60)
    
    # Admin credentials
    ADMIN_EMAIL = "habdilali@admin.com"
    ADMIN_PASSWORD = "H@bdil12345"
    ADMIN_FULL_NAME = "Habdil Ali"
    
    print(f"\nThis will create an admin user with:")
    print(f"  Email: {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Full Name: {ADMIN_FULL_NAME}")
    
    response = input("\nProceed? (y/n): ").lower()
    
    if response == 'y':
        create_admin_user(ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FULL_NAME)
    else:
        print("\n❌ Operation cancelled.")
