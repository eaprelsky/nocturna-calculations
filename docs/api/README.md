# API Documentation Status

## Актуальность документации (на 7 июня 2025)

### ✅ **Актуальные разделы:**

1. **Базовый URL** - обновлен для development и production
2. **Health Check** - добавлен `/health` эндпоинт
3. **Аутентификация** - полностью обновлена:
   - User authentication (15 мин токены)
   - Service authentication (30 дней + eternal)
   - Все auth эндпоинты с правильными путями `/api/auth/*`
4. **Admin эндпоинты** - добавлены все admin функции:
   - `/api/auth/admin/verify`
   - `/api/auth/admin/service-tokens` (CRUD)
   - `/api/auth/admin/registration-settings`
5. **Service Token эндпоинты** - полная документация
6. **Charts эндпоинты** - актуальные пути `/api/charts/*`
7. **Calculations эндпоинты** - актуальные пути `/api/calculations/*`

### ⚠️ **Требует проверки:**

1. **Форматы ответов** - некоторые могут отличаться от реальных
2. **Параметры запросов** - нужно сверить с OpenAPI схемой
3. **Коды ошибок** - проверить актуальные error responses

### 📊 **Статистика покрытия:**

- **Эндпоинты**: ~95% покрыты документацией
- **Аутентификация**: 100% актуальна
- **Admin функции**: 100% документированы
- **Service tokens**: 100% документированы

## Фактические эндпоинты API

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

### Health
- ✅ `GET /health`

## Рекомендации

### Для разработчиков:
1. **Используйте актуальную документацию** в `docs/api/specification.md`
2. **Проверяйте OpenAPI схему** на `/openapi.json` для точных параметров
3. **Тестируйте с реальными токенами** из service token guide

### Для поддержки документации:
1. **Автоматическая генерация** из OpenAPI схемы
2. **Регулярные проверки** соответствия документации и кода
3. **Примеры запросов** с реальными данными

## Полезные ссылки

- **[API Specification](specification.md)** - Полная документация API
- **[Service Token Guide](../guides/service-token-management.md)** - Управление токенами
- **[OpenAPI Schema](http://localhost:8000/openapi.json)** - Актуальная схема
- **[Health Check](http://localhost:8000/health)** - Проверка состояния API 