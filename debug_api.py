#!/usr/bin/env python3
"""
Debug script to test API endpoints and see actual error messages
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_swisseph_directly():
    """Test SwissEph module directly"""
    print("Testing SwissEph module...")
    
    try:
        import swisseph as swe
        print(f"SwissEph version: {swe.version}")
        print(f"Available attributes: {[attr for attr in dir(swe) if not attr.startswith('_')][:20]}")
        
        # Check for flag constants
        flag_attrs = [attr for attr in dir(swe) if 'FLG' in attr or 'SEFLG' in attr]
        print(f"Flag constants: {flag_attrs[:10]}")
        
    except Exception as e:
        print(f"SwissEph error: {e}")
        import traceback
        traceback.print_exc()

def test_core_chart_directly():
    """Test CoreChart creation directly"""
    print("\nTesting CoreChart creation directly...")
    
    try:
        from nocturna_calculations.core.chart import Chart as CoreChart
        
        print("CoreChart imported successfully")
        
        # Try to create chart instance
        chart = CoreChart(
            date="2000-01-01",
            time="12:00:00",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="UTC"
        )
        
        print("CoreChart created successfully")
        
        # Try calling methods
        print("Calling calculate_planetary_positions...")
        planets = chart.calculate_planetary_positions()
        print(f"Planets calculated: {type(planets)}")
        
        print("Calling calculate_houses...")
        houses = chart.calculate_houses()
        print(f"Houses calculated: {type(houses)}")
        
        print("Calling calculate_aspects...")
        aspects = chart.calculate_aspects()
        print(f"Aspects calculated: {type(aspects)}")
        
    except Exception as e:
        print(f"Direct CoreChart error: {e}")
        import traceback
        traceback.print_exc()

def test_natal_chart():
    """Test natal chart creation"""
    print("\nTesting natal chart creation...")
    
    # First, register and login a test user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"debug_{unique_id}@example.com",
        "username": f"debuguser_{unique_id}",
        "password": "TestPassword123!",
        "first_name": "Debug",
        "last_name": "User"
    }
    
    # Register user
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"Register status: {register_response.status_code}")
    if register_response.status_code != 200:
        print(f"Register error: {register_response.text}")
        return
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login error: {login_response.text}")
        return
    
    # Get auth headers
    tokens = login_response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Test natal chart creation
    chart_data = {
        "date": "2000-01-01",
        "time": "12:00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "UTC"
    }
    
    natal_response = requests.post(
        f"{BASE_URL}/api/charts/natal",
        json=chart_data,
        headers=headers
    )
    print(f"Natal chart status: {natal_response.status_code}")
    print(f"Natal chart response: {natal_response.text}")
    
    if natal_response.status_code == 200:
        data = natal_response.json()
        print(f"Response keys: {list(data.keys())}")

def test_planetary_positions():
    """Test planetary positions calculation"""
    print("\nTesting planetary positions...")
    
    # Login with existing user
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "debug_12345@example.com",  # Use a test user
            "password": "TestPassword123!"
        }
    )
    
    if login_response.status_code != 200:
        print("Skipping planetary positions test - no user logged in")
        return
    
    tokens = login_response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    calculation_data = {
        "date": "2000-01-01",
        "time": "12:00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "UTC",
        "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/calculations/planetary-positions",
        json=calculation_data,
        headers=headers
    )
    print(f"Planetary positions status: {response.status_code}")
    print(f"Planetary positions response: {response.text}")

if __name__ == "__main__":
    test_swisseph_directly()
    test_core_chart_directly()
    test_natal_chart()
    test_planetary_positions() 