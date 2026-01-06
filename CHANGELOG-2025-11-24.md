# Changelog - 2025-11-24

## ✅ Synastry & Transit Endpoints - IMPLEMENTED

### Added

**New API Endpoints:**
- `POST /api/charts/{chart_id}/synastry` - Compare two charts
- `POST /api/charts/{chart_id}/transits` - Calculate transits to natal chart

**Core Implementation:**
- `SwissEphAdapter.calculate_synastry_chart()` - Aspect calculation between charts
- Helper methods: `_is_applying()`, `_find_house()`

**Documentation:**
- `docs/guides/synastry-transit-guide.md` - User guide
- `docs/api/specification.md` - Updated API spec (lines 653-799)
- `docs/api/README.md` - Updated endpoint list

**Tests:**
- `tests/api/test_synastry_transit.py` - Comprehensive test suite
- `test_endpoints_manual.py` - Manual testing script

### Fixed

- ❌→✅ Missing synastry endpoint (404)
- ❌→✅ Missing transit endpoint (404)
- ❌→✅ AttributeError in SwissEphAdapter
- ❌→✅ Root endpoint (/) now returns API info
- 📝 Clarified parameter name: `target_chart_id` (not `second_chart_id`)

### Files Modified

**Core:**
- `nocturna_calculations/adapters/swisseph.py` (+190 lines)
- `nocturna_calculations/api/routers/charts.py` (+150 lines)
- `nocturna_calculations/api/schemas.py` (+35 lines)
- `nocturna_calculations/api/app.py` (+25 lines)

**Docs:**
- `docs/api/specification.md` (updated)
- `docs/api/README.md` (updated)
- `docs/README.md` (updated)
- `docs/reports/2025-11-24.md` (fixed)
- `docs/reports/BUG-REPORT-nocturna-calculations.md` (resolved)
- `docs/reports/DOCS-FIX-NEEDED.md` (documented)

**Tests:**
- `tests/api/test_synastry_transit.py` (created)
- `test_endpoints_manual.py` (created)

### Usage

```python
# Synastry
response = client.post(
    f"/api/charts/{chart1_id}/synastry",
    json={"target_chart_id": chart2_id},
    headers={"Authorization": f"Bearer {token}"}
)

# Transits
response = client.post(
    f"/api/charts/{chart_id}/transits",
    json={"transit_date": "2025-11-24", "transit_time": "12:00:00"},
    headers={"Authorization": f"Bearer {token}"}
)
```

### Status

✅ **Ready for production**

- All endpoints working
- Tests passing
- Documentation complete
- No breaking changes

