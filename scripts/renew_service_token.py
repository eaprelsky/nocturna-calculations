#!/usr/bin/env python3
"""
Service Token Renewal Script for Nocturna Calculations

This script renews the service token for API integration with your main backend.
Can be used manually or automated via cron/scheduler.

Usage: python scripts/renew_service_token.py [--check-only] [--days-before-expiry N] [--eternal] [--days N]
"""

import sys
import os
import json
import jwt
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nocturna_calculations.api.models import User
from nocturna_calculations.api.config import settings
from nocturna_calculations.api.routers.auth import create_access_token

class ServiceTokenManager:
    """Manages service token lifecycle"""
    
    def __init__(self):
        self.db = None
        self.setup_database()
        
    def setup_database(self):
        """Initialize database connection"""
        try:
            engine = create_engine(settings.DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.db = SessionLocal()
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    def get_service_user(self):
        """Get the service user account"""
        service_email = os.getenv('SERVICE_USER_EMAIL', 'service@nocturna.internal')
        service_user = self.db.query(User).filter(User.email == service_email).first()
        
        if not service_user:
            print(f"❌ Service user not found: {service_email}")
            print("Run 'make docker-setup-production' first to create service user")
            sys.exit(1)
            
        return service_user
    
    def check_token_expiration(self, token):
        """Check token expiration status"""
        try:
            payload = jwt.decode(token, key="", options={"verify_signature": False})
            exp_timestamp = payload.get('exp')
            
            if not exp_timestamp:
                return None, "Eternal token (no expiration)"
            
            exp_date = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            
            if exp_date < now:
                return 0, f"Token expired on {exp_date}"
            
            days_until_expiry = (exp_date - now).days
            return days_until_expiry, f"Token expires on {exp_date}"
            
        except jwt.DecodeError:
            return None, "Invalid token format"
        except Exception as e:
            return None, f"Error checking token: {e}"
    
    def generate_new_token(self, service_user, days=30, eternal=False):
        """Generate new service token"""
        token_data = {
            "sub": service_user.email,
            "user_id": service_user.id,
            "type": "service"
        }
        
        if eternal:
            # Create token without expiration
            new_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(0)  # Zero duration = eternal token
            )
            expiry_info = "♾️  Eternal (no expiration)"
        else:
            new_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(days=days)
            )
            expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            expiry_info = f"⏰ Expires: {expiry_date} ({days} days)"
        
        return new_token, expiry_info
    
    def update_deployment_summary(self, new_token, old_token=None, expiry_info="30 days"):
        """Update deployment summary with new token"""
        summary_file = project_root / "deployment_summary.json"
        
        summary = {}
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)
        
        # Update summary
        summary.update({
            "token_renewal_date": datetime.utcnow().isoformat(),
            "service_token": new_token[:20] + "...",
            "previous_token": old_token[:20] + "..." if old_token else None,
            "token_expires_info": expiry_info
        })
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary_file
    
    def renew_token(self, days_before_expiry=7, force=False, days=30, eternal=False):
        """Renew service token if needed"""
        print("🔄 Service Token Renewal")
        print("=" * 40)
        
        if eternal:
            print("🔄 Generating eternal token (no expiration)")
            print("⚠️  WARNING: Eternal tokens never expire!")
            print("⚠️  Ensure nginx/firewall restricts external access!")
        elif days != 30:
            print(f"🔄 Generating long-lived token ({days} days)")
        
        # Get current token from environment or deployment summary
        current_token = os.getenv('SERVICE_TOKEN')
        if not current_token:
            summary_file = project_root / "deployment_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                    # This won't have the full token, but we can still check the user
                    print("⚠️  No SERVICE_TOKEN in environment")
            else:
                print("❌ No current token found in environment or deployment summary")
                print("Run 'make docker-setup-production' first")
                return False
        
        # Check if renewal is needed (skip for eternal tokens or force renewal)
        if current_token and not force and not eternal:
            days_left, status_msg = self.check_token_expiration(current_token)
            print(f"📅 Current token status: {status_msg}")
            
            if days_left is None and "Eternal" in status_msg:
                print("✅ Current token is eternal - no renewal needed")
                print("💡 Use --force to generate a new eternal token anyway")
                return True
            elif days_left is None:
                print("⚠️  Unable to check token expiration")
            elif days_left > days_before_expiry:
                print(f"✅ Token still valid for {days_left} days")
                print(f"   Renewal not needed (threshold: {days_before_expiry} days)")
                return True
            elif days_left <= 0:
                print("🚨 Token has expired - generating new token")
            else:
                print(f"⚠️  Token expires in {days_left} days - generating new token")
        else:
            if eternal:
                print("🔄 Eternal token requested")
            elif force:
                print("🔄 Force renewal requested - generating new token")
        
        # Get service user and generate new token
        service_user = self.get_service_user()
        new_token, expiry_info = self.generate_new_token(service_user, days=days, eternal=eternal)
        
        print(f"✅ New service token generated for {service_user.email}")
        print(f"🔐 New token: {new_token[:20]}...")
        print(f"{expiry_info}")
        
        # Update deployment summary
        summary_file = self.update_deployment_summary(new_token, current_token, expiry_info)
        print(f"💾 Updated deployment summary: {summary_file}")
        
        # Print integration instructions
        print("\n📋 Next Steps:")
        print("1. Update your main backend with the new token:")
        print(f"   SERVICE_TOKEN={new_token}")
        print("2. Restart your main backend service")
        print("3. Test API connectivity")
        
        if eternal:
            print("\n🛡️  SECURITY NOTES FOR ETERNAL TOKENS:")
            print("• Eternal tokens NEVER expire - secure them carefully!")
            print("• Restrict API access via nginx/firewall to internal networks only")
            print("• Consider using IP whitelisting for additional security")
            print("• Monitor logs for any suspicious activity")
            print("• Rotate eternal tokens if compromised")
        
        print("\n🔐 IMPORTANT: Save this token securely - it won't be shown again!")
        print(f"Full token: {new_token}")
        
        return True
    
    def check_only(self):
        """Only check token status without renewal"""
        print("🔍 Service Token Status Check")
        print("=" * 35)
        
        current_token = os.getenv('SERVICE_TOKEN')
        if not current_token:
            print("❌ No SERVICE_TOKEN found in environment")
            return False
        
        days_left, status_msg = self.check_token_expiration(current_token)
        print(f"📅 {status_msg}")
        
        if days_left is None and "Eternal" in status_msg:
            print("♾️  Eternal token - no expiration concerns!")
            return True
        elif days_left is None:
            print("⚠️  Unable to determine expiration status")
            return False
        elif days_left <= 0:
            print("🚨 Token has expired - renewal required!")
            return False
        elif days_left <= 7:
            print(f"⚠️  Token expires soon - consider renewal")
            return True
        else:
            print(f"✅ Token is valid")
            return True
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nocturna Service Token Manager")
    parser.add_argument('--check-only', action='store_true',
                       help='Only check token status without renewal')
    parser.add_argument('--days-before-expiry', type=int, default=7,
                       help='Renew token if expiring within N days (default: 7)')
    parser.add_argument('--force', action='store_true',
                       help='Force token renewal regardless of expiration')
    parser.add_argument('--eternal', action='store_true',
                       help='Generate eternal token (never expires) - USE WITH CAUTION!')
    parser.add_argument('--days', type=int, default=30,
                       help='Token validity in days (default: 30, ignored if --eternal)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.eternal and args.days != 30:
        print("⚠️  --days argument ignored when using --eternal")
    
    if args.days < 1:
        print("❌ --days must be at least 1")
        sys.exit(1)
    
    if args.days > 3650:  # 10 years
        print(f"⚠️  {args.days} days is a very long time. Consider using --eternal instead.")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(0)
    
    manager = ServiceTokenManager()
    
    try:
        if args.check_only:
            success = manager.check_only()
        else:
            success = manager.renew_token(
                days_before_expiry=args.days_before_expiry,
                force=args.force,
                days=args.days,
                eternal=args.eternal
            )
        
        return 0 if success else 1
        
    finally:
        manager.close()

if __name__ == '__main__':
    sys.exit(main()) 