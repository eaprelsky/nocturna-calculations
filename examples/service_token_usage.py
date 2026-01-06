#!/usr/bin/env python3
"""
Service Token Usage Example

This example demonstrates how to use the Nocturna service token system
for backend integration with automatic token refresh.

Prerequisites:
1. Admin user created: make admin-create
2. Service token created: make service-token-create
3. API server running: make dev-server

Usage:
    python examples/service_token_usage.py
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nocturna_calculations.client import NocturnaClient
from nocturna_calculations.client.exceptions import (
    TokenExpiredError,
    AuthenticationError,
    APIError
)


def main():
    """Demonstrate service token usage"""
    
    print("🔑 Nocturna Service Token Usage Example")
    print("=" * 50)
    
    # Configuration
    service_token = os.getenv("NOCTURNA_SERVICE_TOKEN")
    api_url = os.getenv("NOCTURNA_API_URL", "http://localhost:8000")
    
    if not service_token:
        print("❌ NOCTURNA_SERVICE_TOKEN environment variable not set")
        print("\nTo create a service token:")
        print("1. make service-token-create")
        print("2. export NOCTURNA_SERVICE_TOKEN=\"your_token_here\"")
        return 1
    
    print(f"API URL: {api_url}")
    print(f"Service Token: {service_token[:20]}...")
    print()
    
    try:
        # Initialize client with auto-refresh
        print("🚀 Initializing Nocturna client...")
        client = NocturnaClient(
            service_token=service_token,
            api_url=api_url,
            auto_refresh=True  # Enable automatic token refresh
        )
        print("✅ Client initialized successfully")
        print()
        
        # Health check
        print("🏥 Checking API health...")
        health = client.health_check()
        print(f"✅ API Status: {health.get('status', 'Unknown')}")
        print()
        
        # Get user info
        print("👤 Getting user information...")
        user_info = client.get_user_info()
        print(f"✅ Authenticated as: {user_info.get('email', 'Unknown')}")
        print(f"   Admin status: {user_info.get('is_superuser', False)}")
        print()
        
        # Example calculations
        print("🌟 Performing astrological calculations...")
        
        # Planetary positions
        print("  📍 Calculating planetary positions...")
        positions = client.calculate_planetary_positions(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,  # Moscow
            longitude=37.6173,
            timezone="Europe/Moscow",
            planets=["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
        )
        
        print(f"     Found {len(positions.get('positions', {}))} planetary positions")
        for planet, data in positions.get('positions', {}).items():
            longitude = data.get('longitude', 0)
            print(f"     {planet}: {longitude:.2f}°")
        print()
        
        # Houses
        print("  🏠 Calculating astrological houses...")
        houses = client.calculate_houses(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow",
            house_system="placidus"
        )
        
        print(f"     Found {len(houses.get('houses', {}))} houses")
        for house_num, cusp in houses.get('houses', {}).items():
            print(f"     House {house_num}: {cusp:.2f}°")
        print()
        
        # Aspects
        print("  🔗 Calculating planetary aspects...")
        aspects = client.calculate_aspects(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow",
            orb_tolerance=8.0
        )
        
        print(f"     Found {len(aspects.get('aspects', []))} aspects")
        for aspect in aspects.get('aspects', [])[:5]:  # Show first 5
            planet1 = aspect.get('planet1', 'Unknown')
            planet2 = aspect.get('planet2', 'Unknown')
            aspect_type = aspect.get('aspect', 'Unknown')
            orb = aspect.get('orb', 0)
            print(f"     {planet1} {aspect_type} {planet2} (orb: {orb:.2f}°)")
        print()
        
        # Create natal chart
        print("  📊 Creating natal chart...")
        chart = client.create_natal_chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow",
            name="Example Chart"
        )
        
        chart_id = chart.get('chart_id', 'Unknown')
        print(f"     Chart created with ID: {chart_id}")
        print()
        
        # Demonstrate token refresh (force refresh)
        print("🔄 Demonstrating token refresh...")
        if client.token_manager:
            old_token = client.token_manager.access_token
            client.token_manager.force_refresh()
            new_token = client.token_manager.access_token
            
            if old_token != new_token:
                print("✅ Token refreshed successfully")
                print(f"   Old token: {old_token[:20] if old_token else 'None'}...")
                print(f"   New token: {new_token[:20] if new_token else 'None'}...")
            else:
                print("ℹ️  Token was already fresh")
        print()
        
        print("🎉 All operations completed successfully!")
        print()
        print("💡 Key Benefits Demonstrated:")
        print("   ✅ Automatic token refresh")
        print("   ✅ Seamless API integration")
        print("   ✅ Error handling and retries")
        print("   ✅ Production-ready authentication")
        
        return 0
        
    except TokenExpiredError as e:
        print(f"❌ Service token expired: {e}")
        print("\nTo create a new service token:")
        print("   make service-token-create")
        return 1
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPlease check:")
        print("   1. Service token is valid")
        print("   2. API server is running")
        print("   3. Admin user exists")
        return 1
        
    except APIError as e:
        print(f"❌ API error: {e}")
        print("\nPlease check:")
        print("   1. API server is running: make dev-server")
        print("   2. Database is set up: make db-migrate")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 