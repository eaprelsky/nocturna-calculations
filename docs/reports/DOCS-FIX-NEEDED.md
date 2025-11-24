# ✅ RESOLVED: Parameter Name in Client Code

**Issue**: Client uses wrong parameter name  
**Status**: Documented (2025-11-24)

## Problem

Client code uses `second_chart_id` but API expects `target_chart_id`

## Solution

In client code change:
```python
# Wrong
payload = {"second_chart_id": chart_id}

# Correct  
payload = {"target_chart_id": chart_id}
```

## API Schema

```python
class SynastryRequest(BaseModel):
    target_chart_id: str  # ✅ Correct name
    orb_multiplier: float = 1.0
```

## Validation Error

```json
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "target_chart_id"],
    "msg": "Field required"
  }]
}
```

**Fix**: Use `target_chart_id` in all synastry requests
