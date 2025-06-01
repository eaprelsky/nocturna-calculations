#!/usr/bin/env python3
"""
Debug script to test API endpoints and see actual error messages
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_calculation_endpoints():
    """Test calculation endpoints that are failing"""
    print("Testing calculation endpoints...")
    
    # Register and login a test user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"calc_debug_{unique_id}@example.com",
        "username": f"calcuser_{unique_id}",
        "password": "TestPassword123!",
        "first_name": "Calc",
        "last_name": "User"
    }
    
    # Register user
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    if register_response.status_code != 200:
        print(f"Register failed: {register_response.text}")
        return
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    tokens = login_response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Test planetary positions
    print("Testing planetary positions...")
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
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Keys: {list(data.keys())}")
    else:
        print(f"Error: {response.text[:200]}...")
    
    # Test aspects
    print("\nTesting aspects...")
    aspects_data = {
        "date": "2000-01-01",
        "time": "12:00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "UTC",
        "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/calculations/aspects",
        json=aspects_data,
        headers=headers
    )
    print(f"Aspects status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Keys: {list(data.keys())}")
    else:
        print(f"Error: {response.text[:200]}...")
    
    # Test houses
    print("\nTesting houses...")
    houses_data = {
        "date": "2000-01-01",
        "time": "12:00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "UTC",
        "house_system": "PLACIDUS"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/calculations/houses",
        json=houses_data,
        headers=headers
    )
    print(f"Houses status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Keys: {list(data.keys())}")
    else:
        print(f"Error: {response.text[:200]}...")

    # Test natal chart
    print("\nTesting natal chart...")
    chart_data = {
        "date": "2000-01-01",
        "time": "12:00:00",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "UTC"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/charts/natal",
        json=chart_data,
        headers=headers
    )
    print(f"Natal chart status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Keys: {list(data.keys())}")
        if "chart_id" in data:
            print(f"chart_id found: {data['chart_id']}")
    else:
        print(f"Error: {response.text[:200]}...")

if __name__ == "__main__":
    test_calculation_endpoints() 