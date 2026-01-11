# API Documentation Status

## Documentation Accuracy (as of June 7, 2025)

### ✅ **Current Sections:**

1. **Base URL** - updated for development and production
2. **Health Check** - `/health` endpoint added
3. **Authentication** - fully updated:
   - User authentication (15 min tokens)
   - Service authentication (30 days + eternal)
   - All auth endpoints with correct paths `/api/auth/*`
4. **Admin Endpoints** - all admin functions added:
   - `/api/auth/admin/verify`
   - `/api/auth/admin/service-tokens` (CRUD)
   - `/api/auth/admin/registration-settings`
5. **Service Token Endpoints** - complete documentation
6. **Charts Endpoints** - current paths `/api/charts/*`
7. **Calculations Endpoints** - current paths `/api/calculations/*`

### ⚠️ **Needs Verification:**

1. **Response Formats** - some may differ from actual responses
2. **Request Parameters** - needs to be cross-checked with OpenAPI schema
3. **Error Codes** - verify actual error responses

### 📊 **Coverage Statistics:**

- **Endpoints**: ~95% covered by documentation
- **Authentication**: 100% up-to-date
- **Admin Functions**: 100% documented
- **Service Tokens**: 100% documented

## Actual API Endpoints

### Authentication
- ✅ `POST /api/auth/register`
- ✅ `POST /api/auth/login`
- ✅ `POST /api/auth/logout`
- ✅ `GET /api/auth/me`
- ✅ `POST /api/auth/refresh`
- ✅ `POST /api/auth/service-token/refresh`

### Admin
- ✅ `GET /api/auth/admin/verify`
- ✅ `GET /api/auth/admin/registration-settings`
- ✅ `GET /api/auth/admin/service-tokens`
- ✅ `POST /api/auth/admin/service-tokens`
- ✅ `DELETE /api/auth/admin/service-tokens/{token_id}`

### Charts
- ✅ `GET /api/charts`
- ✅ `POST /api/charts`
- ✅ `POST /api/charts/natal`
- ✅ `GET /api/charts/{chart_id}`
- ✅ `PUT /api/charts/{chart_id}`
- ✅ `DELETE /api/charts/{chart_id}`
- ✅ `POST /api/charts/{chart_id}/synastry` - Calculate synastry between two charts
- ✅ `POST /api/charts/{chart_id}/transits` - Calculate transits to natal chart

### Calculations (Direct)
- ✅ `POST /api/calculations/planetary-positions`
- ✅ `POST /api/calculations/aspects`
- ✅ `POST /api/calculations/houses`
- ✅ `POST /api/calculations/fixed-stars`
- ✅ `POST /api/calculations/arabic-parts`
- ✅ `POST /api/calculations/dignities`
- ✅ `POST /api/calculations/antiscia`
- ✅ `POST /api/calculations/declinations`
- ✅ `POST /api/calculations/harmonics`
- ✅ `POST /api/calculations/rectification`
- ✅ `POST /api/calculations/primary-directions`
- ✅ `POST /api/calculations/secondary-progressions`

### Calculations (Chart-based)
- ✅ `POST /api/calculations/charts/{chart_id}/positions`
- ✅ `POST /api/calculations/charts/{chart_id}/aspects`
- ✅ `POST /api/calculations/charts/{chart_id}/houses`
- ✅ `POST /api/calculations/charts/{chart_id}/fixed-stars`
- ✅ `POST /api/calculations/charts/{chart_id}/arabic-parts`
- ✅ `POST /api/calculations/charts/{chart_id}/dignities`
- ✅ `POST /api/calculations/charts/{chart_id}/antiscia`
- ✅ `POST /api/calculations/charts/{chart_id}/declinations`
- ✅ `POST /api/calculations/charts/{chart_id}/harmonics`
- ✅ `POST /api/calculations/charts/{chart_id}/rectification`
- ✅ `POST /api/calculations/charts/{chart_id}/synastry`
- ✅ `POST /api/calculations/charts/{chart_id}/progressions`
- ✅ `POST /api/calculations/charts/{chart_id}/directions`
- ✅ `POST /api/calculations/charts/{chart_id}/returns`
- ✅ `POST /api/calculations/charts/{chart_id}/eclipses`
- ✅ `POST /api/calculations/charts/{chart_id}/ingresses`

### Stateless Calculations (NEW - LLM-Optimized)
- ✅ `POST /api/stateless/natal-chart` - Complete natal chart calculation
- ✅ `POST /api/stateless/synastry` - Synastry between two charts
- ✅ `POST /api/stateless/transits` - Transit calculations
- ✅ `POST /api/stateless/progressions` - Secondary progressions
- ✅ `POST /api/stateless/composite` - Composite charts
- ✅ `POST /api/stateless/returns` - Solar/Lunar returns
- ✅ `POST /api/stateless/directions` - Primary directions
- ✅ `POST /api/stateless/eclipses` - Eclipse analysis
- ✅ `POST /api/stateless/ingresses` - Planetary ingresses
- ✅ `POST /api/stateless/fixed-stars` - Fixed stars
- ✅ `POST /api/stateless/arabic-parts` - Arabic parts
- ✅ `POST /api/stateless/dignities` - Essential dignities
- ✅ `POST /api/stateless/antiscia` - Antiscia points
- ✅ `POST /api/stateless/declinations` - Declinations
- ✅ `POST /api/stateless/harmonics` - Harmonic charts
- ✅ `POST /api/stateless/rectification` - Chart rectification

**💡 All stateless endpoints work without database access - perfect for LLM agents!**

### Health
- ✅ `GET /health`

## Recommendations

### For Developers:
1. **Use current documentation** in `docs/api/specification.md`
2. **Check OpenAPI schema** at `/openapi.json` for precise parameters
3. **Test with real tokens** from service token guide

### For Documentation Maintenance:
1. **Automatic generation** from OpenAPI schema
2. **Regular checks** of documentation and code consistency
3. **Request examples** with real data

## Useful Links

- **[API Specification](specification.md)** - Complete API documentation
- **[Stateless API Guide](stateless-api.md)** - 🆕 Stateless API for LLM agents
- **[Service Token Guide](../guides/service-token-management.md)** - Token management
- **[OpenAPI Schema](http://localhost:8000/openapi.json)** - Current schema
- **[Health Check](http://localhost:8000/health)** - API health status 