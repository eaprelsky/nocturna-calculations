#!/usr/bin/env python3
"""
Admin User Creation Script for Nocturna Calculations

This script creates superuser accounts that can access admin functionality.
Usage: python scripts/create_admin.py
"""

import sys
import os
import getpass
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nocturna_calculations.api.models import User
from nocturna_calculations.api.config import settings
from nocturna_calculations.api.routers.auth import get_password_hash

def create_admin_user():
    """Create a new admin user interactively"""
    print("=== Nocturna Calculations - Admin User Creation ===\n")
    
    # Connect to database
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("Make sure your database is running and DATABASE_URL is correct in .env")
        return False
    
    try:
        # Get user input
        print("\n--- Admin User Details ---")
        email = input("Email: ").strip().lower()
        username = input("Username: ").strip()
        first_name = input("First Name (optional): ").strip() or None
        last_name = input("Last Name (optional): ").strip() or None
        
        # Validate input
        if not email or '@' not in email:
            print("❌ Invalid email address")
            return False
        
        if not username:
            print("❌ Username is required")
            return False
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"❌ User already exists with email '{email}' or username '{username}'")
            return False
        
        # Get password securely
        while True:
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Confirm Password: ")
            
            if password != password_confirm:
                print("❌ Passwords don't match. Please try again.")
                continue
            
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long")
                continue
            
            break
        
        # Create admin user
        admin_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_superuser=True  # This makes them an admin
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Superuser: {admin_user.is_superuser}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

def promote_existing_user():
    """Promote an existing user to admin"""
    print("=== Promote Existing User to Admin ===\n")
    
    # Connect to database
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        email_or_username = input("Enter email or username to promote: ").strip()
        
        if not email_or_username:
            print("❌ Email or username is required")
            return False
        
        # Find user
        user = db.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email_or_username}")
            return False
        
        if user.is_superuser:
            print(f"ℹ️  User '{user.email}' is already an admin")
            return True
        
        # Confirm promotion
        print(f"\nFound user:")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Name: {user.first_name} {user.last_name}".strip())
        
        confirm = input("\nPromote this user to admin? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Operation cancelled")
            return False
        
        # Promote user
        user.is_superuser = True
        db.commit()
        
        print(f"✅ User '{user.email}' promoted to admin successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to promote user: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

def list_admin_users():
    """List all admin users"""
    print("=== Current Admin Users ===\n")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    try:
        admins = db.query(User).filter(User.is_superuser == True).all()
        
        if not admins:
            print("No admin users found.")
            return True
        
        print(f"Found {len(admins)} admin user(s):\n")
        for admin in admins:
            print(f"  ID: {admin.id}")
            print(f"  Email: {admin.email}")
            print(f"  Username: {admin.username}")
            print(f"  Name: {admin.first_name} {admin.last_name}".strip())
            print(f"  Created: {admin.created_at}")
            print(f"  Active: {admin.is_active}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list admin users: {e}")
        return False
    
    finally:
        db.close()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    else:
        print("Available actions:")
        print("  1. Create new admin user")
        print("  2. Promote existing user to admin")
        print("  3. List current admin users")
        
        choice = input("\nSelect action (1-3): ").strip()
        action = {'1': 'create', '2': 'promote', '3': 'list'}.get(choice)
    
    if action == 'create':
        success = create_admin_user()
    elif action == 'promote':
        success = promote_existing_user()
    elif action == 'list':
        success = list_admin_users()
    else:
        print("Usage: python scripts/create_admin.py [create|promote|list]")
        return 1
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 