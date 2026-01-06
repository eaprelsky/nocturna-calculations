#!/usr/bin/env python3
"""
Service Token Management Script

This script provides command-line management of service tokens for the Nocturna Calculations API.
Service tokens are long-lived tokens used for backend-to-backend authentication.

Usage:
    python scripts/manage_service_tokens.py create [--days=30] [--scope=calculations] [--eternal]
    python scripts/manage_service_tokens.py list
    python scripts/manage_service_tokens.py revoke <token_id>
    python scripts/manage_service_tokens.py check <token>
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nocturna_calculations.api.config import settings
from nocturna_calculations.api.models import User, Token
from nocturna_calculations.api.routers.auth import create_service_token


class ServiceTokenManager:
    """Manages service token operations"""
    
    def __init__(self):
        self.db = None
        self.setup_database()
        
    def setup_database(self):
        """Initialize database connection"""
        try:
            engine = create_engine(settings.DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.db = SessionLocal()
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    def get_admin_user(self):
        """Get an admin user for token creation"""
        admin_user = self.db.query(User).filter(User.is_superuser == True).first()
        
        if not admin_user:
            print("❌ No admin user found. Create an admin user first:")
            print("   make admin-create")
            sys.exit(1)
            
        return admin_user
    
    def create_token(self, days: int = 30, scope: str = "calculations", eternal: bool = False):
        """Create a new service token"""
        print("🔑 Creating Service Token")
        print("=" * 40)
        
        admin_user = self.get_admin_user()
        
        try:
            jwt_token, token_id = create_service_token(
                user_id=admin_user.id,
                db=self.db,
                days=days,
                scope=scope,
                eternal=eternal
            )
            
            if eternal:
                expires_info = "Never (eternal token)"
                print("⚠️  WARNING: This is an eternal token that never expires!")
            else:
                expires_at = datetime.utcnow() + timedelta(days=days)
                expires_info = f"{expires_at.strftime('%Y-%m-%d %H:%M:%S')} ({days} days)"
            
            print(f"✅ Service token created successfully!")
            print()
            print(f"Token ID:     {token_id}")
            print(f"Scope:        {scope}")
            print(f"Expires:      {expires_info}")
            print(f"Created by:   {admin_user.email}")
            print()
            print("🔐 SERVICE TOKEN:")
            print("-" * 80)
            print(jwt_token)
            print("-" * 80)
            print()
            print("💡 Usage in your application:")
            print(f'   export NOCTURNA_SERVICE_TOKEN="{jwt_token}"')
            print()
            print("🔄 Auto-refresh endpoint:")
            print("   POST /api/auth/service-token/refresh")
            print("   Authorization: Bearer <service_token>")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create service token: {e}")
            return False
    
    def list_tokens(self):
        """List all service tokens"""
        print("📋 Service Tokens")
        print("=" * 60)
        
        try:
            tokens = self.db.query(Token).filter(
                Token.token_type == "service"
            ).order_by(Token.created_at.desc()).all()
            
            if not tokens:
                print("No service tokens found.")
                return True
            
            print(f"Found {len(tokens)} service token(s):\n")
            
            for token in tokens:
                user = self.db.query(User).filter(User.id == token.user_id).first()
                is_expired = token.expires_at < datetime.utcnow()
                
                if is_expired:
                    status = "❌ EXPIRED"
                elif token.expires_at.year > 2100:  # Eternal token
                    status = "♾️  ETERNAL"
                else:
                    days_left = (token.expires_at - datetime.utcnow()).days
                    if days_left <= 7:
                        status = f"⚠️  EXPIRES IN {days_left} DAYS"
                    else:
                        status = f"✅ ACTIVE ({days_left} days left)"
                
                print(f"  ID: {token.id}")
                print(f"  Status: {status}")
                print(f"  Scope: {token.scope}")
                print(f"  Created: {token.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Expires: {token.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Created by: {user.email if user else 'Unknown'}")
                print(f"  Last used: {token.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if token.last_used_at else 'Never'}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to list service tokens: {e}")
            return False
    
    def revoke_token(self, token_id: str):
        """Revoke a service token"""
        print(f"🗑️  Revoking Service Token: {token_id}")
        print("=" * 50)
        
        try:
            token = self.db.query(Token).filter(
                Token.id == token_id,
                Token.token_type == "service"
            ).first()
            
            if not token:
                print(f"❌ Service token not found: {token_id}")
                return False
            
            user = self.db.query(User).filter(User.id == token.user_id).first()
            
            print(f"Token found:")
            print(f"  Scope: {token.scope}")
            print(f"  Created: {token.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Created by: {user.email if user else 'Unknown'}")
            print()
            
            confirm = input("Are you sure you want to revoke this token? [y/N]: ")
            if confirm.lower() != 'y':
                print("❌ Revocation cancelled")
                return False
            
            self.db.delete(token)
            self.db.commit()
            
            print("✅ Service token revoked successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to revoke service token: {e}")
            return False
    
    def check_token(self, token: str):
        """Check token validity and information"""
        print("🔍 Token Information")
        print("=" * 40)
        
        try:
            # Decode token without verification first to get basic info
            payload = jwt.decode(token, key="", options={"verify_signature": False, "verify_exp": False})
            
            print("📄 Token Payload:")
            print(f"  User ID: {payload.get('sub', 'N/A')}")
            print(f"  Type: {payload.get('type', 'N/A')}")
            print(f"  Scope: {payload.get('scope', 'N/A')}")
            print(f"  Token ID: {payload.get('token_id', 'N/A')}")
            
            # Check expiration
            exp_timestamp = payload.get('exp')
            if exp_timestamp:
                exp_date = datetime.fromtimestamp(exp_timestamp)
                now = datetime.utcnow()
                
                if exp_date < now:
                    print(f"  Status: ❌ EXPIRED ({exp_date.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    days_left = (exp_date - now).days
                    print(f"  Status: ✅ VALID (expires in {days_left} days)")
                    print(f"  Expires: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"  Status: ♾️  ETERNAL (no expiration)")
            
            # Verify signature
            try:
                jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                print(f"  Signature: ✅ VALID")
            except JWTError as e:
                print(f"  Signature: ❌ INVALID ({e})")
            
            # Check database record if it's a service token
            if payload.get('type') == 'service' and payload.get('token_id'):
                db_token = self.db.query(Token).filter(
                    Token.id == payload.get('token_id'),
                    Token.token_type == "service"
                ).first()
                
                if db_token:
                    print(f"  Database: ✅ FOUND")
                    print(f"  Last used: {db_token.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if db_token.last_used_at else 'Never'}")
                else:
                    print(f"  Database: ❌ NOT FOUND (token may have been revoked)")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to check token: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Manage Nocturna service tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create 30-day token for calculations
  python scripts/manage_service_tokens.py create
  
  # Create 90-day token with admin scope
  python scripts/manage_service_tokens.py create --days 90 --scope "calculations,admin"
  
  # Create eternal token (never expires)
  python scripts/manage_service_tokens.py create --eternal
  
  # List all tokens
  python scripts/manage_service_tokens.py list
  
  # Revoke a token
  python scripts/manage_service_tokens.py revoke abc123-def456-ghi789
  
  # Check token validity
  python scripts/manage_service_tokens.py check "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new service token')
    create_parser.add_argument('--days', type=int, default=30, help='Token expiration in days (default: 30)')
    create_parser.add_argument('--scope', default='calculations', help='Token scope (default: calculations)')
    create_parser.add_argument('--eternal', action='store_true', help='Create eternal token (never expires)')
    
    # List command
    subparsers.add_parser('list', help='List all service tokens')
    
    # Revoke command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke a service token')
    revoke_parser.add_argument('token_id', help='Token ID to revoke')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check token validity')
    check_parser.add_argument('token', help='JWT token to check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = ServiceTokenManager()
    
    if args.command == 'create':
        success = manager.create_token(
            days=args.days,
            scope=args.scope,
            eternal=args.eternal
        )
    elif args.command == 'list':
        success = manager.list_tokens()
    elif args.command == 'revoke':
        success = manager.revoke_token(args.token_id)
    elif args.command == 'check':
        success = manager.check_token(args.token)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main()) 