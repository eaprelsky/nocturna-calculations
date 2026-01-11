# LLM Integration Quick Start

## Overview

Nocturna Calculations now fully supports **stateless mode** - all calculations are available without database access. This makes the service an ideal "Swiss Army knife" for astrological LLM agents.

## What Changed?

### Before (with database):
```
1. POST /api/charts/natal → create chart, get chart_id
2. POST /api/charts/{chart_id}/transits → use chart_id
```

### Now (stateless):
```
1. POST /api/stateless/transits → pass all data in one request
```

## Available Endpoints

All endpoints are located at `/api/stateless/*`:

| Endpoint | Description |
|----------|-------------|
| `/natal-chart` | Natal chart calculation |
| `/synastry` | Synastry (compatibility) |
| `/transits` | Transit calculations |
| `/progressions` | Secondary progressions |
| `/composite` | Composite charts |
| `/returns` | Solar/Lunar returns |
| `/directions` | Primary directions |
| `/eclipses` | Eclipse analysis |
| `/ingresses` | Planetary ingresses |
| `/fixed-stars` | Fixed stars |
| `/arabic-parts` | Arabic parts |
| `/dignities` | Essential dignities |
| `/antiscia` | Antiscia points |
| `/declinations` | Declinations |
| `/harmonics` | Harmonic charts |
| `/rectification` | Chart rectification |

## Quick Start

### 1. Start the Server

```bash
# Development
make dev

# Docker
make docker-up
```

### 2. Get Authentication Token

```bash
# Create service token
curl -X POST http://localhost:8000/api/auth/admin/service-tokens \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "LLM Agent Token", "expires_in_days": 365}'
```

### 3. Use Stateless API

```python
import requests

# Example: calculate natal chart
response = requests.post(
    "http://localhost:8000/api/stateless/natal-chart",
    headers={"Authorization": "Bearer <your_token>"},
    json={
        "date": "1990-01-15",
        "time": "14:30:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York"
    }
)

print(response.json())
```

## Usage Examples

### Python Client

See `examples/llm_agent_usage.py` for complete client example.

### OpenAI Function Calling

```python
functions = [
    {
        "name": "calculate_natal_chart",
        "description": "Calculate astrology natal chart",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "time": {"type": "string"},
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["date", "time", "latitude", "longitude"]
        }
    }
]
```

### Anthropic Claude Tools

```python
tools = [
    {
        "name": "calculate_transits",
        "description": "Calculate planetary transits",
        "input_schema": {
            "type": "object",
            "properties": {
                "natal_chart": {"type": "object"},
                "transit_date": {"type": "string"},
                "transit_time": {"type": "string"}
            },
            "required": ["natal_chart", "transit_date", "transit_time"]
        }
    }
]
```

## Stateless API Benefits

✅ **Zero Database Latency** - pure calculations  
✅ **Horizontal Scaling** - each instance is independent  
✅ **LLM-Optimized** - perfect for function calling  
✅ **Karmic Points Included** - North Node, South Node, Lilith included by default  
✅ **Backward Compatible** - legacy endpoints still work  
✅ **Simple Integration** - one request = one result  

## Special Features

### Karmic Points

All planetary calculations now include karmic points by default:
- **North Node (Rahu)** - Evolutionary direction, life path
- **South Node (Ketu)** - Past life patterns, release points
- **Black Moon Lilith** - Shadow self, repressed desires

For selective calculation with both mean and true variants:
```bash
POST /api/stateless/special-points
```

See [Special Karmic Points](../api/stateless-api.md#17-special-karmic-points) documentation.

## Next Steps

1. Explore [complete documentation](../api/stateless-api.md)
2. Try [examples](../../examples/llm_agent_usage.py)
3. Integrate with your LLM agent

## Support

- GitHub: [nocturna-calculations](https://github.com/eaprelsky/nocturna-calculations)
- Email: yegor.aprelsky@gmail.com
