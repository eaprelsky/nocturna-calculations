"""
Manual test script for synastry and transit endpoints
Run this after starting the server with: make run
"""
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api"

def test_root_endpoint():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def register_user():
    """Register a test user and get token"""
    print("\n=== Registering Test User ===")
    user_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"User registered: {data.get('id')}")
            return data.get("access_token")
        elif response.status_code == 400:
            # User might already exist, try to login
            print("User might exist, trying login...")
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            response = requests.post(
                f"{API_URL}/auth/token",
                data=login_data
            )
            if response.status_code == 200:
                return response.json().get("access_token")
        
        print(f"Response: {response.json()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_chart(token, date, time, lat, lon, tz="UTC"):
    """Create a natal chart"""
    print(f"\n=== Creating Chart: {date} {time} ===")
    chart_data = {
        "date": date,
        "time": time,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_URL}/charts/natal",
            json=chart_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            chart_id = data.get("chart_id")
            print(f"Chart created: {chart_id}")
            return chart_id
        else:
            print(f"Error: {response.json()}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_synastry(token, chart1_id, chart2_id):
    """Test synastry endpoint"""
    print("\n=== Testing Synastry Endpoint ===")
    
    synastry_request = {
        "target_chart_id": chart2_id,
        "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
        "orb_multiplier": 1.0
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_URL}/charts/{chart1_id}/synastry",
            json=synastry_request,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('data'):
                aspects = data['data'].get('aspects', [])
                print(f"Found {len(aspects)} aspects")
                if aspects:
                    print("First 3 aspects:")
                    for aspect in aspects[:3]:
                        print(f"  - {aspect.get('planet1')} {aspect.get('aspect_type')} {aspect.get('planet2')} (orb: {aspect.get('orb'):.2f}°)")
                print(f"Total strength: {data['data'].get('total_strength', 'N/A')}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_transit(token, chart_id):
    """Test transit endpoint"""
    print("\n=== Testing Transit Endpoint ===")
    
    now = datetime.now()
    transit_request = {
        "transit_date": now.strftime("%Y-%m-%d"),
        "transit_time": now.strftime("%H:%M:%S"),
        "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
        "orb_multiplier": 1.0
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{API_URL}/charts/{chart_id}/transits",
            json=transit_request,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('data'):
                positions = data['data'].get('transit_positions', {})
                print(f"Transit positions calculated: {len(positions)} planets")
                aspects = data['data'].get('aspects', [])
                print(f"Found {len(aspects)} transit aspects")
                if aspects:
                    print("First 3 transit aspects:")
                    for aspect in aspects[:3]:
                        print(f"  - {aspect.get('planet1')} {aspect.get('aspect_type')} {aspect.get('planet2')} (orb: {aspect.get('orb'):.2f}°)")
                print(f"Total strength: {data['data'].get('total_strength', 'N/A')}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("Nocturna Calculations API - Synastry & Transit Test")
    print("="*60)
    
    # Test basic endpoints
    if not test_root_endpoint():
        print("❌ Root endpoint failed")
        return
    
    if not test_health_endpoint():
        print("❌ Health check failed")
        return
    
    # Register user and get token
    token = register_user()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    print(f"\n✅ Authentication successful")
    
    # Create two charts for synastry
    chart1_id = create_chart(
        token,
        date="1985-03-10",
        time="01:34:00",
        lat=55.0288307,
        lon=82.9226887,
        tz="Asia/Novosibirsk"
    )
    
    if not chart1_id:
        print("❌ Failed to create first chart")
        return
    
    chart2_id = create_chart(
        token,
        date="1990-07-15",
        time="14:20:00",
        lat=55.0288307,
        lon=82.9226887,
        tz="Asia/Novosibirsk"
    )
    
    if not chart2_id:
        print("❌ Failed to create second chart")
        return
    
    # Test synastry
    if test_synastry(token, chart1_id, chart2_id):
        print("\n✅ Synastry endpoint working correctly")
    else:
        print("\n❌ Synastry endpoint failed")
    
    # Test transit
    if test_transit(token, chart1_id):
        print("\n✅ Transit endpoint working correctly")
    else:
        print("\n❌ Transit endpoint failed")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    main()

