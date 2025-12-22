"""
Generate bcrypt hash for admin password using app.auth
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.auth import get_password_hash

# Password to hash
password = "H@bdil12345"

# Generate hash
hashed = get_password_hash(password)

print("=" * 60)
print("PASSWORD HASH GENERATOR")
print("=" * 60)
print(f"\nOriginal Password: {password}")
print(f"\nBcrypt Hash:\n{hashed}")
print("\n" + "=" * 60)
print("\nUse this hash in your SQL seed file:")
print("=" * 60)
