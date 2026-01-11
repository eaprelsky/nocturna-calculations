# Stateless API Guide

## Overview

The Stateless API provides a complete set of astrological calculation endpoints that work **without database access**. All required data is passed directly in the request body, making it ideal for:

- **LLM Agent Integration** - Perfect for function calling in AI applications
- **Microservices Architecture** - No shared database dependency
- **High-Performance Computing** - Zero database latency
- **Horizontal Scaling** - Each instance is completely independent
- **External Tool Integration** - Use as a Swiss Army knife for astrology calculations

## Key Features

✅ **100% Stateless** - No database or session storage required  
✅ **Complete Functionality** - All features available (natal, synastry, transits, progressions, etc.)  
✅ **LLM-Optimized** - Designed for easy function calling by AI agents  
✅ **Backward Compatible** - Original database-backed endpoints remain available  
✅ **RESTful Design** - Clean, predictable API structure  

## Base URL

```
/api/stateless
```

## Authentication

All endpoints require authentication via Bearer token:

```bash
Authorization: Bearer <your_token>
```

## Common Data Structures

### ChartDataInput

Basic chart data structure used across all endpoints:

```json
{
  "date": "1990-01-15",
  "time": "14:30:00",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York",
  "house_system": "PLACIDUS"
}
```

**Fields:**
- `date` (string, required): Date in YYYY-MM-DD format
- `time` (string, required): Time in HH:MM:SS format
- `latitude` (float, required): Latitude in degrees (-90 to 90)
- `longitude` (float, required): Longitude in degrees (-180 to 180)
- `timezone` (string, optional): Timezone identifier (default: "UTC")
- `house_system` (string, optional): House system (default: "PLACIDUS")

### StatelessCalculationOptions

Optional calculation parameters:

```json
{
  "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"],
  "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
  "orb_multiplier": 1.0
}
```

## Endpoints

### 1. Natal Chart Calculation

Calculate a complete natal chart without saving to database.

**Endpoint:** `POST /api/stateless/natal-chart`

**Request:**
```json
{
  "date": "1990-01-15",
  "time": "14:30:00",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York",
  "house_system": "PLACIDUS"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "planets": { ... },
    "houses": { ... },
    "aspects": { ... }
  }
}
```

**Use Case:** Quick chart generation, temporary calculations, testing.

---

### 2. Synastry Analysis

Compare two natal charts for relationship compatibility.

**Endpoint:** `POST /api/stateless/synastry`

**Request:**
```json
{
  "chart1": {
    "date": "1990-01-15",
    "time": "14:30:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "chart2": {
    "date": "1992-06-20",
    "time": "09:15:00",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "timezone": "America/Los_Angeles"
  },
  "options": {
    "orb_multiplier": 1.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "aspects": [...],
    "compatibility_score": 0.75
  }
}
```

**Use Case:** Relationship analysis, compatibility reports, dating app integrations.

---

### 3. Transit Calculations

Calculate current planetary transits to a natal chart.

**Endpoint:** `POST /api/stateless/transits`

**Request:**
```json
{
  "natal_chart": {
    "date": "1990-01-15",
    "time": "14:30:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "transit_date": "2026-01-11",
  "transit_time": "12:00:00",
  "options": {
    "orb_multiplier": 0.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transit_positions": { ... },
    "aspects": [...],
    "active_transits": [...]
  }
}
```

**Use Case:** Daily horoscopes, timing predictions, event planning.

---

### 4. Secondary Progressions

Calculate progressed chart for a given date.

**Endpoint:** `POST /api/stateless/progressions`

**Request:**
```json
{
  "natal_chart": {
    "date": "1990-01-15",
    "time": "14:30:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "progression_date": "2026-01-11",
  "progression_type": "secondary",
  "options": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "progressed_positions": { ... },
    "aspects_to_natal": [...]
  }
}
```

**Use Case:** Long-term forecasting, personal development analysis.

---

### 5. Composite Charts

Create a composite chart from two natal charts.

**Endpoint:** `POST /api/stateless/composite`

**Request:**
```json
{
  "chart1": { ... },
  "chart2": { ... },
  "composite_type": "midpoint",
  "options": {}
}
```

**Composite Types:**
- `midpoint` - Midpoint composite
- `davison` - Davison relationship chart

---

### 6. Planetary Returns

Calculate solar, lunar, or planetary returns.

**Endpoint:** `POST /api/stateless/returns`

**Request:**
```json
{
  "natal_chart": { ... },
  "return_date": "2026-01-15",
  "return_type": "solar",
  "planet": "SUN",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Return Types:**
- `solar` - Solar return (annual)
- `lunar` - Lunar return (monthly)
- `planetary` - Planetary return (specify planet)

---

### 7. Primary Directions

Calculate primary or symbolic directions.

**Endpoint:** `POST /api/stateless/directions`

**Request:**
```json
{
  "natal_chart": { ... },
  "target_date": "2026-01-11",
  "direction_type": "primary",
  "key_rate": 1.0
}
```

---

### 8. Eclipse Analysis

Find eclipses and their impact on natal chart.

**Endpoint:** `POST /api/stateless/eclipses`

**Request:**
```json
{
  "natal_chart": { ... },
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "eclipse_type": "all"
}
```

**Eclipse Types:**
- `solar` - Solar eclipses only
- `lunar` - Lunar eclipses only
- `all` - Both types

---

### 9. Planetary Ingresses

Calculate when planets change signs.

**Endpoint:** `POST /api/stateless/ingresses`

**Request:**
```json
{
  "natal_chart": { ... },
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
}
```

---

### 10. Fixed Stars

Calculate fixed star positions and conjunctions.

**Endpoint:** `POST /api/stateless/fixed-stars`

**Request:**
```json
{
  "chart_data": { ... },
  "orb": 1.0,
  "magnitude_limit": 2.0
}
```

---

### 11. Arabic Parts

Calculate Arabic parts (lots).

**Endpoint:** `POST /api/stateless/arabic-parts`

**Request:**
```json
{
  "chart_data": { ... },
  "parts": ["FORTUNE", "SPIRIT", "EROS"]
}
```

**Common Parts:**
- `FORTUNE` - Part of Fortune
- `SPIRIT` - Part of Spirit
- `EROS` - Part of Eros

---

### 12. Essential Dignities

Calculate planetary dignities and debilities.

**Endpoint:** `POST /api/stateless/dignities`

**Request:**
```json
{
  "chart_data": { ... },
  "dignity_system": "traditional"
}
```

**Dignity Systems:**
- `traditional` - Classical rulerships
- `modern` - Modern rulerships with outer planets

---

### 13. Antiscia

Calculate antiscia and contra-antiscia points.

**Endpoint:** `POST /api/stateless/antiscia`

**Request:**
```json
{
  "chart_data": { ... },
  "include_contra": true
}
```

---

### 14. Declinations

Calculate declinations and parallel aspects.

**Endpoint:** `POST /api/stateless/declinations`

**Request:**
```json
{
  "chart_data": { ... },
  "parallel_orb": 1.0
}
```

---

### 15. Harmonic Charts

Calculate harmonic charts.

**Endpoint:** `POST /api/stateless/harmonics`

**Request:**
```json
{
  "chart_data": { ... },
  "harmonics": [2, 3, 4, 5, 7, 9]
}
```

---

### 16. Chart Rectification

Refine birth time based on life events.

**Endpoint:** `POST /api/stateless/rectification`

**Request:**
```json
{
  "chart_data": { ... },
  "events": [
    {
      "date": "2010-05-15",
      "description": "Marriage",
      "type": "major"
    }
  ],
  "time_range_minutes": 120
}
```

---

## LLM Function Calling Examples

### OpenAI Function Calling

```python
functions = [
    {
        "name": "calculate_natal_chart",
        "description": "Calculate a complete natal astrology chart",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Birth date YYYY-MM-DD"},
                "time": {"type": "string", "description": "Birth time HH:MM:SS"},
                "latitude": {"type": "number", "description": "Birth latitude"},
                "longitude": {"type": "number", "description": "Birth longitude"},
                "timezone": {"type": "string", "description": "Timezone"}
            },
            "required": ["date", "time", "latitude", "longitude"]
        }
    },
    {
        "name": "calculate_synastry",
        "description": "Calculate relationship compatibility between two people",
        "parameters": {
            "type": "object",
            "properties": {
                "person1": {"$ref": "#/definitions/chart_data"},
                "person2": {"$ref": "#/definitions/chart_data"}
            },
            "required": ["person1", "person2"]
        }
    }
]
```

### Anthropic Claude Tool Use

```python
tools = [
    {
        "name": "calculate_transits",
        "description": "Calculate current planetary transits to natal chart",
        "input_schema": {
            "type": "object",
            "properties": {
                "natal_chart": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "time": {"type": "string"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    }
                },
                "transit_date": {"type": "string"},
                "transit_time": {"type": "string"}
            },
            "required": ["natal_chart", "transit_date", "transit_time"]
        }
    }
]
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "data": null,
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

## Rate Limiting

No rate limiting on stateless endpoints currently. Each request is independent and doesn't consume persistent resources.

## Performance Considerations

- **Response Time:** ~100-500ms per calculation (depending on complexity)
- **Concurrency:** Fully concurrent, no database bottleneck
- **Caching:** Can implement client-side caching as all inputs are explicit
- **Batch Processing:** Submit parallel requests for better throughput

## Migration from Database-Backed API

### Before (with database):
```bash
# Create chart
POST /api/charts/natal
# Later use chart_id
POST /api/charts/{chart_id}/transits
```

### After (stateless):
```bash
# One-shot calculation
POST /api/stateless/transits
# Pass all data in single request
```

## Best Practices

1. **Validation:** Always validate input dates/coordinates before sending
2. **Error Handling:** Implement retry logic for transient failures
3. **Caching:** Cache results on client side when appropriate
4. **Batch Operations:** Use parallel requests for multiple independent calculations
5. **Timezone Handling:** Always specify timezone explicitly

## Support

For issues or questions:
- GitHub Issues: [nocturna-calculations/issues](https://github.com/eaprelsky/nocturna-calculations/issues)
- Email: yegor.aprelsky@gmail.com

## Next Steps

- Explore [API Reference](./reference.md) for detailed schemas
- Check [Service Integration Guide](../guides/service-integration.md)
- Try [Example Implementations](../examples/)
