# Synastry and Transit Calculation Guide

This guide explains how to use the synastry and transit calculation endpoints in the Nocturna Calculations API.

## Overview

The API provides two powerful endpoints for comparative astrological analysis:

1. **Synastry**: Compare two natal charts (relationship compatibility)
2. **Transits**: Calculate current planetary influences on a natal chart

## Synastry Calculations

### What is Synastry?

Synastry is the comparison of two natal charts to analyze the relationship dynamics between two individuals. It shows how the planets in one person's chart interact with the planets in another person's chart.

### Endpoint

```http
POST /api/charts/{chart_id}/synastry
```

### Usage Example

```python
import requests

# API configuration
API_URL = "https://calculations.nocturna.ru/api"
AUTH_TOKEN = "your_auth_token_here"

# Chart IDs (obtained from creating charts)
natal_chart_id = "9bb8c84d-4d7a-4c3d-a099-c10d53392909"
partner_chart_id = "448a4760-062b-4de6-bd37-54c43e22557a"

# Synastry request
synastry_request = {
    "target_chart_id": partner_chart_id,
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
    "orb_multiplier": 1.0
}

# Make request
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
response = requests.post(
    f"{API_URL}/charts/{natal_chart_id}/synastry",
    json=synastry_request,
    headers=headers
)

synastry_data = response.json()
```

### Response Structure

```json
{
    "success": true,
    "data": {
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "aspect_type": "trine",
                "orb": 2.5,
                "applying": true,
                "strength": 0.85
            }
        ],
        "total_strength": 0.72,
        "planet_aspects": {
            "SUN": ["trine_MOON", "square_MARS"],
            "MOON": ["trine_SUN"]
        },
        "house_aspects": {
            "1": ["conjunction_VENUS"],
            "7": ["opposition_MARS"]
        }
    },
    "error": null
}
```

### Interpreting Results

- **aspects**: List of all aspects between the two charts
  - `planet1`: Planet from the first chart (natal)
  - `planet2`: Planet from the second chart (comparison)
  - `aspect_type`: Type of aspect (conjunction, trine, etc.)
  - `orb`: Deviation from exact aspect in degrees
  - `strength`: Aspect strength (0-1, higher is stronger)

- **total_strength**: Overall compatibility score (0-1)
  - 0.0 - 0.3: Challenging relationship
  - 0.3 - 0.5: Mixed dynamics
  - 0.5 - 0.7: Good compatibility
  - 0.7 - 1.0: Excellent compatibility

## Transit Calculations

### What are Transits?

Transits are the current positions of planets in the sky and how they aspect your natal chart. They represent current influences and energies affecting you at any given time.

### Endpoint

```http
POST /api/charts/{chart_id}/transits
```

### Usage Example

```python
import requests
from datetime import datetime

# API configuration
API_URL = "https://calculations.nocturna.ru/api"
AUTH_TOKEN = "your_auth_token_here"

# Natal chart ID
natal_chart_id = "9bb8c84d-4d7a-4c3d-a099-c10d53392909"

# Get current date/time
now = datetime.now()

# Transit request
transit_request = {
    "transit_date": now.strftime("%Y-%m-%d"),
    "transit_time": now.strftime("%H:%M:%S"),
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
    "orb_multiplier": 1.0
}

# Make request
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
response = requests.post(
    f"{API_URL}/charts/{natal_chart_id}/transits",
    json=transit_request,
    headers=headers
)

transit_data = response.json()
```

### Response Structure

```json
{
    "success": true,
    "data": {
        "transit_positions": {
            "SUN": {
                "longitude": 359.5,
                "latitude": 0.0,
                "distance": 0.983,
                "speed": 0.985,
                "is_retrograde": false
            },
            "MARS": {
                "longitude": 123.4,
                "latitude": 1.2,
                "distance": 1.523,
                "speed": 0.65,
                "is_retrograde": true
            }
        },
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "natal_MOON",
                "aspect_type": "conjunction",
                "orb": 1.2,
                "applying": true,
                "strength": 0.92
            }
        ],
        "total_strength": 0.68,
        "planet_aspects": {
            "SUN": ["conjunction_natal_MOON"],
            "MARS": ["square_natal_SUN"]
        }
    },
    "error": null
}
```

### Interpreting Results

- **transit_positions**: Current positions of all planets
  - `is_retrograde`: Whether the planet is moving backward

- **aspects**: Aspects between transiting and natal planets
  - `planet1`: Transiting planet
  - `planet2`: Natal planet (prefixed with "natal_")
  - `applying`: Whether the aspect is getting stronger (true) or weaker (false)

- **total_strength**: Overall transit influence (0-1)

## Common Use Cases

### 1. Relationship Compatibility

```python
# Calculate synastry between two people
synastry = calculate_synastry(person1_chart_id, person2_chart_id)

# Analyze key aspects
for aspect in synastry["data"]["aspects"]:
    if aspect["strength"] > 0.7:
        print(f"Strong {aspect['aspect_type']} between {aspect['planet1']} and {aspect['planet2']}")
```

### 2. Daily Transit Check

```python
# Get today's transits
from datetime import datetime

now = datetime.now()
transits = calculate_transits(
    natal_chart_id,
    transit_date=now.strftime("%Y-%m-%d"),
    transit_time=now.strftime("%H:%M:%S")
)

# Check for important transits
for aspect in transits["data"]["aspects"]:
    if aspect["aspect_type"] in ["conjunction", "opposition"]:
        print(f"Important transit: {aspect['planet1']} {aspect['aspect_type']} {aspect['planet2']}")
```

### 3. Custom Orb Settings

```python
# Use tighter orbs for more precise aspects
transit_request = {
    "transit_date": "2025-11-24",
    "transit_time": "12:00:00",
    "orb_multiplier": 0.5  # Half the default orbs
}
```

## Best Practices

1. **Orb Multiplier**: 
   - Use 1.0 for standard orbs
   - Use 0.5-0.7 for tighter, more significant aspects
   - Use 1.2-1.5 for wider orbs and more aspects

2. **Aspect Selection**:
   - Include major aspects (conjunction, opposition, trine, square, sextile) for general analysis
   - Add minor aspects (semisextile, quincunx, etc.) for detailed work

3. **Transit Timing**:
   - Check transits at the same time daily for consistency
   - Pay attention to applying vs. separating aspects
   - Monitor retrograde planets closely

4. **Synastry Interpretation**:
   - Focus on aspects with strength > 0.7 for key dynamics
   - Consider both harmonious (trine, sextile) and challenging (square, opposition) aspects
   - Look at house placements for areas of life affected

## Error Handling

```python
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    if not result.get("success"):
        print(f"Calculation error: {result.get('error')}")
    else:
        # Process successful result
        process_data(result["data"])
        
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Chart not found")
    elif e.response.status_code == 401:
        print("Authentication required")
    else:
        print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Rate Limiting

Both endpoints respect standard API rate limits:
- 100 requests per minute for authenticated users
- 10 requests per minute for service tokens

## Additional Resources

- [API Specification](../api/specification.md) - Complete API documentation
- [API Reference](../api/reference.md) - Core calculation methods
- [User Quickstart Guide](user-quickstart.md) - Getting started with the API
- [Service Integration Guide](service-integration.md) - Backend integration

## Support

For issues or questions:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review [API Examples](../examples/)
- Contact support: support@nocturna.ru

