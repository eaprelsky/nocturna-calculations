# Solar Return API Issues (staging)

**Date**: 2026-01-11
**API**: `https://stage.calc.nocturna.ru/api/stateless/returns`
**Status**: 🔴 Critical bugs found

## Issues Found

### 1. Incorrect return_time (CRITICAL)

**Request**:
```json
{
  "natal_chart": {
    "date": "1990-01-15",
    "time": "14:30:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "return_date": "2026-01-15",
  "return_type": "solar",
  "planet": "SUN",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Response**:
```json
{
  "return_time": "1990-01-27T07:59:38",  // WRONG! Should be 2026
  ...
}
```

**Expected**: `"return_time": "2026-01-15T..."`
**Actual**: `"return_time": "1990-01-27T07:59:38"`

### 2. Numeric Planet Indices Instead of Names

**Response**:
```json
{
  "planets": {
    "0": {...},  // Should be "SUN"
    "1": {...},  // Should be "MOON"
    "2": {...},  // Should be "MERCURY"
    ...
  }
}
```

**Expected**: Planet names as strings (`"SUN"`, `"MOON"`, etc.)
**Actual**: Swiss Ephemeris numeric indices (`"0"`, `"1"`, etc.)

**Mapping**:
- 0 = SUN
- 1 = MOON
- 2 = MERCURY
- 3 = VENUS
- 4 = MARS
- 5 = JUPITER
- 6 = SATURN
- 7 = URANUS
- 8 = NEPTUNE
- 9 = PLUTO

### 3. Missing Karmic Points (Vedic Astrology)

**Response includes only**: SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN, URANUS, NEPTUNE, PLUTO (10 planets)

**Missing**:
- ❌ **Раху (RAHU)** - Северный лунный узел - index 10 or 11
- ❌ **Кету (KETU)** - Южный лунный узел - index 13 (противоположность Раху)
- ❌ **Лилит (LILITH)** - Черная Луна - index 12
- ❌ **Селена (SELENA)** - Белая Луна (противоположность Лилит)

According to documentation, these should be **included by default**.

### 4. Houses Format Inconsistency

**Response**:
```json
{
  "houses": {
    "cusps": [244.80, 277.14, ...],  // Array of 12 cusps
    "angles": [...],
    "system": "PLACIDUS"
  }
}
```

**Old API format**:
```json
{
  "houses": [
    {"number": 1, "longitude": 244.80},
    {"number": 2, "longitude": 277.14},
    ...
  ]
}
```

Need to document the correct format or provide conversion.

## Test Results

**API Response includes:**
- ✅ Planets 0-9 (SUN through PLUTO)
- ✅ Houses with cusps and angles
- ✅ Retrograde status calculated correctly
- ❌ **NO karmic points** (indices 10-13 missing)

**Expected but missing:**
- Index 10: RAHU (North Node)
- Index 11: KETU (South Node) 
- Index 12: LILITH (Black Moon)
- Index 13: SELENA (White Moon)

## Impact

- 🔴 **CRITICAL**: Solar return calculations show wrong year (1990 instead of 2026) - users will get completely incorrect predictions
- 🔴 **CRITICAL**: Missing karmic points (Rahu, Ketu, Lilith, Selena) - incomplete Vedic astrology analysis
- ✅ **RESOLVED**: Planet names mapping implemented in client code

## Workarounds Implemented

1. **Planet index mapping** - Added `PLANET_INDEX_MAP` in `NocturnaClient`
2. **Format conversion** - Added `_convert_planets_dict_to_list()` method
3. **return_time validation** - Need to add validation and error handling

## Required Fixes (Server Side)

1. Fix `return_time` calculation to use target year, not natal year
2. Use planet names instead of numeric indices in response
3. Include North Node, Lilith, and Selena by default
4. Document the correct houses format

## Testing

```bash
# Run integration test
python scripts/test_solar_return_integration.py

# Expected output after fixes:
# - return_time: 2026-01-15T... (not 1990)
# - planets: SUN, MOON, ..., NORTH_NODE, LILITH
# - 12+ planets total
```

## References

- API Documentation: `third-party-docs/nocturna-calculations/api/stateless-api.md`
- Test script: `scripts/test_solar_return_integration.py`
- Client implementation: `src/api/nocturna_client.py`
