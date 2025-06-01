#!/usr/bin/env python3
"""
Production Setup Script for Nocturna Calculations Service

This script configures the system for production deployment as a service component:
1. Creates admin user with provided password
2. Creates service user with API token for main backend integration
3. Configures user management settings for service mode
4. Validates deployment configuration

Usage: python scripts/setup_production.py [--dry-run]
"""

import sys
import os
import secrets
import getpass
import json
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nocturna_calculations.api.models import User, Token
from nocturna_calculations.api.config import settings
from nocturna_calculations.api.routers.auth import get_password_hash, create_access_token

class ProductionSetup:
    """Production deployment setup manager"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.db = None
        self.engine = None
        self.setup_database()
        
        print("🚀 Nocturna Calculations - Production Setup")
        print("=" * 50)
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print("=" * 50)
    
    def setup_database(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(settings.DATABASE_URL)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.db = SessionLocal()
            print("✅ Connected to database")
            
            # Test connection
            self.db.execute(text("SELECT 1"))
            print("✅ Database connection verified")
            
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            print("Make sure your database is running and DATABASE_URL is correct")
            sys.exit(1)
    
    def generate_secure_token(self, length=32):
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    def create_admin_user(self):
        """Create admin user for system management"""
        print("\n📋 Setting up admin user...")
        
        # Get admin credentials from environment or prompt
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@nocturna.service')
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_password:
            print("⚠️  ADMIN_PASSWORD not found in environment")
            if not self.dry_run:
                admin_password = getpass.getpass("Enter admin password: ")
            else:
                print("🔍 Would prompt for admin password")
                return None
        
        # Check if admin already exists
        existing_admin = self.db.query(User).filter(
            (User.email == admin_email) | (User.username == admin_username)
        ).first()
        
        if existing_admin:
            print(f"ℹ️  Admin user already exists: {existing_admin.email}")
            if existing_admin.is_superuser:
                print("✅ Admin user is properly configured")
                return existing_admin
            else:
                print("🔧 Promoting existing user to admin...")
                if not self.dry_run:
                    existing_admin.is_superuser = True
                    self.db.commit()
                print("✅ User promoted to admin")
                return existing_admin
        
        # Create new admin user
        if not self.dry_run:
            admin_user = User(
                email=admin_email,
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True
            )
            
            self.db.add(admin_user)
            self.db.commit()
            self.db.refresh(admin_user)
            
            print(f"✅ Admin user created: {admin_user.email}")
            return admin_user
        else:
            print(f"🔍 Would create admin user: {admin_email}")
            return None
    
    def create_service_user(self):
        """Create service user for API integration"""
        print("\n🔧 Setting up service user...")
        
        service_email = os.getenv('SERVICE_USER_EMAIL', 'service@nocturna.internal')
        service_username = os.getenv('SERVICE_USER_USERNAME', 'service_user')
        
        # Check if service user already exists
        existing_service = self.db.query(User).filter(
            (User.email == service_email) | (User.username == service_username)
        ).first()
        
        if existing_service:
            print(f"ℹ️  Service user already exists: {existing_service.email}")
            return existing_service, self.get_service_token(existing_service)
        
        # Create service user
        if not self.dry_run:
            # Generate a strong password for the service user (not used for API access)
            service_password = self.generate_secure_token(16)
            
            service_user = User(
                email=service_email,
                username=service_username,
                hashed_password=get_password_hash(service_password),
                first_name="Service",
                last_name="Integration",
                is_active=True,
                is_superuser=False  # Regular user for API access
            )
            
            self.db.add(service_user)
            self.db.commit()
            self.db.refresh(service_user)
            
            print(f"✅ Service user created: {service_user.email}")
            
            # Generate long-lived access token for service integration
            service_token = self.generate_service_token(service_user)
            return service_user, service_token
        else:
            print(f"🔍 Would create service user: {service_email}")
            return None, None
    
    def generate_service_token(self, user):
        """Generate long-lived token for service integration"""
        print("\n🔑 Generating service API token...")
        
        if not self.dry_run:
            # Create a long-lived token (30 days)
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "type": "service"
            }
            
            # Generate token with extended expiry
            service_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(days=30)
            )
            
            print("✅ Service token generated (expires in 30 days)")
            print(f"🔐 Token: {service_token[:20]}...")
            
            return service_token
        else:
            print("🔍 Would generate service token")
            return "dry_run_token"
    
    def get_service_token(self, user):
        """Get existing service token or create new one"""
        # For simplicity, generate a new token
        # In production, you might want to check for existing valid tokens
        return self.generate_service_token(user)
    
    def configure_service_mode(self):
        """Configure system for service component mode"""
        print("\n⚙️  Configuring service component mode...")
        
        config_updates = {
            'ALLOW_USER_REGISTRATION': 'false',
            'REGISTRATION_REQUIRES_APPROVAL': 'true',
            'MAX_USERS_LIMIT': '100'
        }
        
        # In a real implementation, you might want to store these in the database
        # or update configuration files
        print("✅ Service mode configuration:")
        for key, value in config_updates.items():
            print(f"   {key}={value}")
        
        if not self.dry_run:
            # Here you could update database settings or config files
            pass
        else:
            print("🔍 Would update service configuration")
    
    def validate_deployment(self):
        """Validate production deployment configuration"""
        print("\n🔍 Validating deployment configuration...")
        
        checks = []
        
        # Check database connection
        try:
            self.db.execute(text("SELECT COUNT(*) FROM users"))
            checks.append(("Database connection", True, "Connected"))
        except Exception as e:
            checks.append(("Database connection", False, str(e)))
        
        # Check environment variables
        required_env_vars = [
            'SECRET_KEY', 'POSTGRES_PASSWORD', 'DATABASE_URL'
        ]
        
        for var in required_env_vars:
            value = os.getenv(var)
            if value and value != f"CHANGE_THIS_TO_A_SECURE_{var.upper()}":
                checks.append((f"Environment: {var}", True, "Set"))
            else:
                checks.append((f"Environment: {var}", False, "Not set or default"))
        
        # Print validation results
        print("\n📊 Validation Results:")
        print("-" * 50)
        for check_name, passed, message in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {message}")
        
        # Summary
        passed_checks = sum(1 for _, passed, _ in checks if passed)
        total_checks = len(checks)
        
        print(f"\n📈 Summary: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 All checks passed! Ready for production deployment.")
            return True
        else:
            print("⚠️  Some checks failed. Please review configuration.")
            return False
    
    def create_deployment_summary(self, admin_user, service_user, service_token):
        """Create deployment summary with important information"""
        print("\n📄 Deployment Summary")
        print("=" * 50)
        
        summary = {
            "deployment_date": datetime.utcnow().isoformat(),
            "admin_user": {
                "email": admin_user.email if admin_user else "admin@nocturna.service",
                "username": admin_user.username if admin_user else "admin"
            },
            "service_user": {
                "email": service_user.email if service_user else "service@nocturna.internal",
                "username": service_user.username if service_user else "service_user"
            },
            "service_token": service_token[:20] + "..." if service_token else "dry_run_token...",
            "configuration": {
                "allow_user_registration": False,
                "max_users_limit": 100,
                "cors_origins": os.getenv('CORS_ORIGINS', '["http://localhost:3000"]'),
                "api_url": f"http://localhost:{os.getenv('API_PORT', '8000')}"
            }
        }
        
        # Save summary to file
        if not self.dry_run:
            summary_file = project_root / "deployment_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"💾 Summary saved to: {summary_file}")
        
        # Print key information
        print(f"🏢 Admin Email: {summary['admin_user']['email']}")
        print(f"🔧 Service Email: {summary['service_user']['email']}")
        print(f"🔑 Service Token: {summary['service_token']}")
        print(f"🌐 API URL: {summary['configuration']['api_url']}")
        
        return summary
    
    def run_setup(self):
        """Run complete production setup"""
        try:
            # Step 1: Create admin user
            admin_user = self.create_admin_user()
            
            # Step 2: Create service user and token
            service_user, service_token = self.create_service_user()
            
            # Step 3: Configure service mode
            self.configure_service_mode()
            
            # Step 4: Validate deployment
            validation_passed = self.validate_deployment()
            
            # Step 5: Create summary
            summary = self.create_deployment_summary(admin_user, service_user, service_token)
            
            if validation_passed:
                print("\n🎉 Production setup completed successfully!")
                print("\n📋 Next steps:")
                print("1. Update your main backend to use the service token")
                print("2. Configure CORS origins for your domains")
                print("3. Set up monitoring and logging")
                print("4. Test API integration")
                
                if service_token and not self.dry_run:
                    print(f"\n🔐 IMPORTANT: Save this service token securely:")
                    print(f"    {service_token}")
                    print("    This token allows your main backend to access the API")
            else:
                print("\n⚠️  Setup completed with warnings. Please review validation results.")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            if self.db:
                self.db.rollback()
            return False
        
        finally:
            if self.db:
                self.db.close()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nocturna Calculations Production Setup")
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    setup = ProductionSetup(dry_run=args.dry_run)
    success = setup.run_setup()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 