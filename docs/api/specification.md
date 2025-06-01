# Nocturna Calculations API Specification

## Base URL

```
https://api.nocturna-calculations.com/v1
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Architecture Overview

The Nocturna Calculations API features a **hybrid architecture** supporting two complementary calculation approaches:

### Direct Calculations (`/calculations/*`)
**Stateless operations** for quick calculations without chart persistence.

**Use Cases:**
- Real-time planetary position lookups
- Quick aspect calculations  
- Mobile app integrations
- Microservice calls
- One-off calculations

**Benefits:**
- Lower latency (no database lookups)
- Stateless operations
- Easier integration
- Perfect for simple calculations

### Chart-Based Calculations (`/charts/{chart_id}/*`)
**Stateful operations** using stored chart data for complex workflows.

**Use Cases:**
- Personal natal chart analysis
- Progression tracking over time
- User-specific calculation preferences
- Complex multi-chart operations
- Historical analysis

**Benefits:**
- Chart data persistence
- User preferences and settings
- Caching for repeated calculations
- Advanced features requiring reference data

## Common Response Format

```json
{
    "success": true,
    "data": {},
    "error": null,
    "meta": {
        "timestamp": "2024-03-20T12:00:00Z",
        "request_id": "req_123456"
    }
}
```

## Error Response Format

```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input parameters",
        "details": {
            "field": "date",
            "reason": "Invalid date format"
        }
    },
    "meta": {
        "timestamp": "2024-03-20T12:00:00Z",
        "request_id": "req_123456"
    }
}
```

## Endpoints

### Authentication

#### Register User

```http
POST /auth/register
```

Request:

```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
}
```

Response:

```json
{
    "success": true,
    "data": {
        "user_id": "usr_123456",
        "email": "user@example.com",
        "username": "username",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2024-03-20T12:00:00Z"
    }
}
```

#### Login

```http
POST /auth/login
```

Request:

```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```

Response:

```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "expires_in": 3600
    }
}
```

#### Refresh Token

```http
POST /auth/refresh
```

Request:

```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:

```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "expires_in": 3600
    }
}
```

#### Logout

```http
POST /auth/logout
```

Response:

```json
{
    "success": true,
    "data": null
}
```

### Charts

#### Create Chart

```http
POST /charts
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "config": {
        "house_system": "PLACIDUS",
        "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
        "orbs": {
            "conjunction": 10.0,
            "opposition": 10.0,
            "trine": 8.0,
            "square": 8.0,
            "sextile": 6.0
        }
    }
}
```

Response:

```json
{
    "success": true,
    "data": {
        "chart_id": "chr_123456",
        "date": "2024-03-20T12:00:00+03:00",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "timezone": "Europe/Moscow",
        "config": {
            "house_system": "PLACIDUS",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
            "orbs": {
                "conjunction": 10.0,
                "opposition": 10.0,
                "trine": 8.0,
                "square": 8.0,
                "sextile": 6.0
            }
        },
        "created_at": "2024-03-20T12:00:00Z"
    }
}
```

#### Get Chart

```http
GET /charts/{chart_id}
```

Response:

```json
{
    "success": true,
    "data": {
        "chart_id": "chr_123456",
        "date": "2024-03-20T12:00:00+03:00",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "timezone": "Europe/Moscow",
        "config": {
            "house_system": "PLACIDUS",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
            "orbs": {
                "conjunction": 10.0,
                "opposition": 10.0,
                "trine": 8.0,
                "square": 8.0,
                "sextile": 6.0
            }
        },
        "created_at": "2024-03-20T12:00:00Z"
    }
}
```

#### Update Chart

```http
PUT /charts/{chart_id}
```

Request:

```json
{
    "config": {
        "house_system": "KOCH",
        "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"]
    }
}
```

Response:

```json
{
    "success": true,
    "data": {
        "chart_id": "chr_123456",
        "date": "2024-03-20T12:00:00+03:00",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "timezone": "Europe/Moscow",
        "config": {
            "house_system": "KOCH",
            "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"],
            "orbs": {
                "conjunction": 10.0,
                "opposition": 10.0,
                "trine": 8.0
            }
        },
        "updated_at": "2024-03-20T12:00:00Z"
    }
}
```

#### Delete Chart

```http
DELETE /charts/{chart_id}
```

Response:

```json
{
    "success": true,
    "data": null
}
```

#### List Charts

```http
GET /charts
```

Query Parameters:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)
- `sort_by`: Sort field (default: created_at)
- `sort_order`: Sort order (asc/desc, default: desc)

Response:

```json
{
    "success": true,
    "data": {
        "charts": [
            {
                "chart_id": "chr_123456",
                "date": "2024-03-20T12:00:00+03:00",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "timezone": "Europe/Moscow",
                "created_at": "2024-03-20T12:00:00Z"
            }
        ],
        "pagination": {
            "total": 100,
            "page": 1,
            "per_page": 20,
            "total_pages": 5
        }
    }
}
```

## Direct Calculations

The Direct Calculations API provides stateless calculation endpoints that don't require chart persistence. These endpoints are perfect for quick calculations, real-time applications, and scenarios where you don't need to store chart data.

### Planetary Positions

```http
POST /calculations/planetary-positions
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"],
    "include_retrograde": true,
    "include_speed": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": [
            {
                "planet": "SUN",
                "longitude": 359.5,
                "latitude": 0.0,
                "distance": 0.983,
                "speed": 0.985,
                "is_retrograde": false,
                "sign": "PISCES",
                "degree": 29,
                "minute": 30,
                "second": 0
            }
        ]
    }
}
```

### Aspects

```http
POST /calculations/aspects
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
    "orb_multiplier": 1.0
}
```

Response:

```json
{
    "success": true,
    "data": {
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "aspect_type": "CONJUNCTION",
                "orb": 0.7,
                "applying": true,
                "exact_time": "2024-03-20T12:30:00Z"
            }
        ]
    }
}
```

### Houses

```http
POST /calculations/houses
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "house_system": "PLACIDUS",
    "include_angles": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "houses": [
            {
                "number": 1,
                "longitude": 45.2,
                "latitude": 0.0,
                "sign": "TAURUS",
                "degree": 15,
                "minute": 12,
                "second": 0
            }
        ]
    }
}
```

### Fixed Stars

```http
POST /calculations/fixed-stars
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "stars": ["ALDEBARAN", "REGULUS", "SPICA"],
    "include_conjunctions": true,
    "orb": 1.0
}
```

Response:

```json
{
    "success": true,
    "data": {
        "stars": {
            "ALDEBARAN": {
                "longitude": 69.7,
                "latitude": -5.5,
                "magnitude": 0.87,
                "conjunctions": [
                    {
                        "planet": "SUN",
                        "orb": 0.3
                    }
                ]
            }
        }
    }
}
```

### Arabic Parts

```http
POST /calculations/arabic-parts
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "parts": ["FORTUNA", "SPIRIT", "VICTORY"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "parts": {
            "FORTUNA": {
                "longitude": 123.4,
                "aspects": [
                    {
                        "planet": "MOON",
                        "angle": 120.0,
                        "orb": 3.4,
                        "aspect_type": "TRINE"
                    }
                ]
            }
        }
    }
}
```

### Dignities

```http
POST /calculations/dignities
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_scores": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "dignities": {
            "SUN": {
                "rulership": 5,
                "exaltation": 0,
                "detriment": -5,
                "fall": 0,
                "triplicity": 3,
                "term": 2,
                "face": 1,
                "total_score": 6
            }
        }
    }
}
```

### Antiscia

```http
POST /calculations/antiscia
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "antiscia": {
            "SUN": {
                "longitude": 180.5,
                "latitude": -0.0,
                "aspects": [
                    {
                        "planet": "MOON",
                        "angle": 90.0,
                        "orb": 2.3,
                        "aspect_type": "SQUARE"
                    }
                ]
            }
        }
    }
}
```

### Declinations

```http
POST /calculations/declinations
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_parallels": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "declinations": {
            "SUN": {
                "declination": -0.5,
                "parallels": [
                    {
                        "planet": "MOON",
                        "orb": 0.3
                    }
                ]
            }
        }
    }
}
```

### Harmonics

```http
POST /calculations/harmonics
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "harmonic": 2,
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": {
            "SUN": {
                "longitude": 359.0,
                "latitude": 0.0
            }
        },
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "angle": 90.0,
                "orb": 1.2,
                "aspect_type": "SQUARE"
            }
        ]
    }
}
```

### Rectification

```http
POST /calculations/rectification
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "events": [
        {
            "date": "2024-03-20T12:00:00Z",
            "type": "MARRIAGE",
            "description": "Wedding day"
        }
    ],
    "time_window": {
        "start": "2024-03-20T10:00:00Z",
        "end": "2024-03-20T14:00:00Z"
    },
    "method": "EVENT_BASED",
    "parameters": {
        "direction_method": "SEMI_ARC",
        "aspect_types": ["CONJUNCTION", "OPPOSITION", "TRINE"]
    }
}
```

Response:

```json
{
    "success": true,
    "data": {
        "rectified_time": "2024-03-20T11:23:45Z",
        "confidence": 0.85,
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "ASC",
                "angle": 0.0,
                "orb": 0.5,
                "aspect_type": "CONJUNCTION"
            }
        ],
        "events_matched": 3,
        "total_events": 3
    }
}
```

### Primary Directions

```http
POST /calculations/primary-directions
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "target_date": "2024-03-20T12:00:00Z",
    "method": "SEMI_ARC",
    "include_converse": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "directions": [
            {
                "planet": "SUN",
                "angle": 45.2,
                "arc": 1.2,
                "type": "DIRECT"
            }
        ],
        "converse": [
            {
                "planet": "SUN",
                "angle": 315.2,
                "arc": 1.2,
                "type": "CONVERSE"
            }
        ]
    }
}
```

### Secondary Progressions

```http
POST /calculations/secondary-progressions
```

Request:

```json
{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "target_date": "2024-03-20T12:00:00Z",
    "type": "SECONDARY",
    "include_returns": true,
    "include_angles": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": {
            "SUN": {
                "longitude": 45.2,
                "latitude": 0.0
            }
        },
        "angles": {
            "ASC": 45.2,
            "MC": 135.8
        },
        "returns": {
            "solar": {
                "date": "2024-03-20T12:00:00Z",
                "positions": {
                    "SUN": {
                        "longitude": 0.0,
                        "latitude": 0.0
                    }
                }
            }
        }
    }
}
```

## Chart-Based Calculations

Chart-Based Calculations use stored chart data to provide enhanced functionality, caching, and user-specific preferences. These endpoints are ideal for personal chart analysis, tracking progressions over time, and complex multi-chart operations.

### Planetary Positions

```http
POST /charts/{chart_id}/positions
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"],
    "include_retrograde": true,
    "include_speed": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": [
            {
                "planet": "SUN",
                "longitude": 359.5,
                "latitude": 0.0,
                "distance": 0.983,
                "speed": 0.985,
                "is_retrograde": false,
                "house": 12,
                "sign": "PISCES",
                "degree": 29,
                "minute": 30,
                "second": 0
            }
        ]
    }
}
```

### Aspects

```http
POST /charts/{chart_id}/aspects
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
    "orb_multiplier": 1.0
}
```

Response:

```json
{
    "success": true,
    "data": {
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "aspect_type": "CONJUNCTION",
                "orb": 0.7,
                "applying": true,
                "exact_time": "2024-03-20T12:30:00Z"
            }
        ]
    }
}
```

### Houses

```http
POST /charts/{chart_id}/houses
```

Request:

```json
{
    "house_system": "PLACIDUS",
    "include_angles": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "houses": [
            {
                "number": 1,
                "longitude": 45.2,
                "latitude": 0.0,
                "sign": "TAURUS",
                "degree": 15,
                "minute": 12,
                "second": 0
            }
        ],
        "angles": {
            "ASC": 45.2,
            "MC": 135.8,
            "DESC": 225.2,
            "IC": 315.8
        }
    }
}
```

### Fixed Stars

```http
POST /charts/{chart_id}/fixed-stars
```

Request:

```json
{
    "stars": ["ALDEBARAN", "REGULUS", "SPICA"],
    "include_conjunctions": true,
    "orb": 1.0
}
```

Response:

```json
{
    "success": true,
    "data": {
        "stars": {
            "ALDEBARAN": {
                "longitude": 69.7,
                "latitude": -5.5,
                "magnitude": 0.87,
                "conjunctions": [
                    {
                        "planet": "SUN",
                        "orb": 0.3
                    }
                ]
            }
        }
    }
}
```

### Arabic Parts

```http
POST /charts/{chart_id}/arabic-parts
```

Request:

```json
{
    "parts": ["FORTUNA", "SPIRIT", "VICTORY"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "parts": {
            "FORTUNA": {
                "longitude": 123.4,
                "house": 5,
                "aspects": [
                    {
                        "planet": "MOON",
                        "angle": 120.0,
                        "orb": 3.4,
                        "aspect_type": "TRINE"
                    }
                ]
            }
        }
    }
}
```

### Dignities

```http
POST /charts/{chart_id}/dignities
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_scores": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "dignities": {
            "SUN": {
                "rulership": 5,
                "exaltation": 0,
                "detriment": -5,
                "fall": 0,
                "triplicity": 3,
                "term": 2,
                "face": 1,
                "total_score": 6
            }
        }
    }
}
```

### Antiscia

```http
POST /charts/{chart_id}/antiscia
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "antiscia": {
            "SUN": {
                "longitude": 180.5,
                "latitude": -0.0,
                "house": 6,
                "aspects": [
                    {
                        "planet": "MOON",
                        "angle": 90.0,
                        "orb": 2.3,
                        "aspect_type": "SQUARE"
                    }
                ]
            }
        }
    }
}
```

### Declinations

```http
POST /charts/{chart_id}/declinations
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_parallels": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "declinations": {
            "SUN": {
                "declination": -0.5,
                "parallels": [
                    {
                        "planet": "MOON",
                        "orb": 0.3
                    }
                ]
            }
        }
    }
}
```

### Harmonics

```http
POST /charts/{chart_id}/harmonics
```

Request:

```json
{
    "harmonic": 2,
    "planets": ["SUN", "MOON", "MERCURY", "VENUS"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": {
            "SUN": {
                "longitude": 359.0,
                "latitude": 0.0
            }
        },
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "angle": 90.0,
                "orb": 1.2,
                "aspect_type": "SQUARE"
            }
        ]
    }
}
```

### Rectification

```http
POST /charts/{chart_id}/rectification
```

Request:

```json
{
    "events": [
        {
            "date": "2024-03-20T12:00:00Z",
            "type": "MARRIAGE",
            "description": "Wedding day"
        }
    ],
    "time_window": {
        "start": "2024-03-20T10:00:00Z",
        "end": "2024-03-20T14:00:00Z"
    },
    "method": "EVENT_BASED",
    "parameters": {
        "direction_method": "SEMI_ARC",
        "aspect_types": ["CONJUNCTION", "OPPOSITION", "TRINE"]
    }
}
```

Response:

```json
{
    "success": true,
    "data": {
        "rectified_time": "2024-03-20T11:23:45Z",
        "confidence": 0.85,
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "ASC",
                "angle": 0.0,
                "orb": 0.5,
                "aspect_type": "CONJUNCTION"
            }
        ],
        "events_matched": 3,
        "total_events": 3
    }
}
```

## Advanced Calculations

### Synastry

```http
POST /charts/{chart_id}/synastry
```

Request:

```json
{
    "target_chart_id": "chr_789012",
    "include_composite": true,
    "include_davison": true,
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"],
    "orb_multiplier": 1.0
}
```

Response:

```json
{
    "success": true,
    "data": {
        "aspects": [
            {
                "planet1": "SUN",
                "planet2": "MOON",
                "angle": 120.0,
                "orb": 2.3,
                "aspect_type": "TRINE",
                "applying": true
            }
        ],
        "composite": {
            "chart_id": "chr_comp_123456",
            "positions": {
                "SUN": {
                    "longitude": 45.2,
                    "latitude": 0.0
                }
            }
        },
        "davison": {
            "chart_id": "chr_dav_123456",
            "positions": {
                "SUN": {
                    "longitude": 45.2,
                    "latitude": 0.0
                }
            }
        }
    }
}
```

### Progressions

```http
POST /charts/{chart_id}/progressions
```

Request:

```json
{
    "target_date": "2024-03-20T12:00:00Z",
    "type": "SECONDARY",
    "include_returns": true,
    "include_angles": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": {
            "SUN": {
                "longitude": 45.2,
                "latitude": 0.0
            }
        },
        "angles": {
            "ASC": 45.2,
            "MC": 135.8
        },
        "returns": {
            "solar": {
                "date": "2024-03-20T12:00:00Z",
                "positions": {
                    "SUN": {
                        "longitude": 0.0,
                        "latitude": 0.0
                    }
                }
            }
        }
    }
}
```

### Directions

```http
POST /charts/{chart_id}/directions
```

Request:

```json
{
    "target_date": "2024-03-20T12:00:00Z",
    "type": "PRIMARY",
    "method": "SEMI_ARC",
    "include_converse": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "directions": [
            {
                "planet": "SUN",
                "angle": 45.2,
                "arc": 1.2,
                "type": "DIRECT"
            }
        ],
        "converse": [
            {
                "planet": "SUN",
                "angle": 315.2,
                "arc": 1.2,
                "type": "CONVERSE"
            }
        ]
    }
}
```

### Returns

```http
POST /charts/{chart_id}/returns
```

Request:

```json
{
    "start_date": "2024-03-20T12:00:00Z",
    "end_date": "2025-03-20T12:00:00Z",
    "types": ["SOLAR", "LUNAR"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "returns": {
            "solar": [
                {
                    "date": "2024-03-20T12:00:00Z",
                    "positions": {
                        "SUN": {
                            "longitude": 0.0,
                            "latitude": 0.0
                        }
                    },
                    "aspects": [
                        {
                            "planet1": "SUN",
                            "planet2": "MOON",
                            "angle": 120.0,
                            "orb": 2.3,
                            "aspect_type": "TRINE"
                        }
                    ]
                }
            ]
        }
    }
}
```

### Eclipses

```http
POST /charts/{chart_id}/eclipses
```

Request:

```json
{
    "start_date": "2024-03-20T12:00:00Z",
    "end_date": "2025-03-20T12:00:00Z",
    "types": ["SOLAR", "LUNAR"],
    "include_aspects": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "eclipses": {
            "solar": [
                {
                    "date": "2024-04-08T18:17:00Z",
                    "type": "TOTAL",
                    "magnitude": 1.056,
                    "positions": {
                        "SUN": {
                            "longitude": 19.0,
                            "latitude": 0.0
                        },
                        "MOON": {
                            "longitude": 19.0,
                            "latitude": 0.0
                        }
                    },
                    "aspects": [
                        {
                            "planet1": "SUN",
                            "planet2": "MARS",
                            "angle": 90.0,
                            "orb": 2.3,
                            "aspect_type": "SQUARE"
                        }
                    ]
                }
            ]
        }
    }
}
```

### Ingresses

```http
POST /charts/{chart_id}/ingresses
```

Request:

```json
{
    "start_date": "2024-03-20T12:00:00Z",
    "end_date": "2025-03-20T12:00:00Z",
    "types": ["SIGN", "HOUSE"],
    "include_retrograde": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "ingresses": {
            "sign": [
                {
                    "planet": "SUN",
                    "sign": "ARIES",
                    "date": "2024-03-20T12:00:00Z",
                    "is_retrograde": false
                }
            ],
            "house": [
                {
                    "planet": "SUN",
                    "house": 1,
                    "date": "2024-03-20T12:00:00Z",
                    "is_retrograde": false
                }
            ]
        }
    }
}
```

## Usage Examples

### Quick Planetary Position Lookup (Direct)
```bash
curl -X POST "https://api.nocturna-calculations.com/v1/calculations/planetary-positions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "planets": ["SUN", "MOON"]
  }'
```

### Personal Chart Analysis (Chart-Based)
```bash
# First create a chart
curl -X POST "https://api.nocturna-calculations.com/v1/charts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1990-05-15T14:30:00Z",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  }'

# Then use the chart for multiple calculations
curl -X POST "https://api.nocturna-calculations.com/v1/charts/chr_123456/positions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"planets": ["SUN", "MOON", "ASC", "MC"]}'
```

## Use Case Guide

### When to Use Direct Calculations (`/calculations/*`)

Direct calculations are ideal for **stateless, one-time calculations** where you don't need to store chart data.

#### 📱 **Mobile App Real-Time Updates**
```bash
# Get current planetary positions for a location
curl -X POST "/calculations/planetary-positions" \
  -d '{
    "date": "2024-03-20",
    "time": "14:30:00", 
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS"]
  }'
```
**Benefits:**
- ✅ **Instant results** - no database overhead
- ✅ **Perfect for widgets** showing "current sky"
- ✅ **Lightweight** - minimal server resources
- ✅ **Stateless** - no authentication complexity

#### ⚡ **API Integration for Other Services**
```bash
# Microservice calculating aspects for external system
curl -X POST "/calculations/aspects" \
  -d '{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "aspects": ["CONJUNCTION", "OPPOSITION"]
  }'
```
**Benefits:**
- ✅ **Easy integration** - simple request/response
- ✅ **No user management** needed
- ✅ **Scalable** - can handle high volume
- ✅ **Fast** - optimized for speed

#### 🔍 **Quick Lookups and Validations**
```bash
# Check if Mars is retrograde on a specific date
curl -X POST "/calculations/planetary-positions" \
  -d '{
    "date": "2024-03-20",
    "time": "12:00:00",
    "latitude": 0,
    "longitude": 0,
    "planets": ["MARS"]
  }'
```

### When to Use Chart-Based Calculations (`/charts/{chart_id}/*`)

Chart-based calculations are ideal for **personal analysis, tracking over time, and complex workflows**.

#### 👤 **Personal Natal Chart Analysis**
```bash
# Step 1: Create and store personal chart
curl -X POST "/charts" \
  -d '{
    "date": "1990-05-15T14:30:00Z",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "config": {
      "house_system": "WHOLE_SIGN",
      "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE", "QUINCUNX"],
      "orbs": {"conjunction": 8.0, "opposition": 8.0}
    }
  }'

# Step 2: Get planetary positions with house information
curl -X POST "/charts/chr_123456/positions" \
  -d '{"planets": ["SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN"]}'

# Step 3: Calculate aspects using stored preferences
curl -X POST "/charts/chr_123456/aspects" \
  -d '{}'  # Uses chart's configured aspects and orbs

# Step 4: Analyze progressions for current year
curl -X POST "/charts/chr_123456/progressions" \
  -d '{
    "target_date": "2024-03-20T12:00:00Z",
    "type": "SECONDARY", 
    "include_returns": true
  }'
```
**Benefits:**
- ✅ **Personalized settings** - custom orbs, house systems
- ✅ **House information** included in planetary positions
- ✅ **Caching** - faster repeated calculations
- ✅ **User preferences** stored and reused
- ✅ **Historical tracking** - track changes over time

#### 💕 **Relationship Compatibility Analysis**
```bash
# Step 1: Create charts for both partners
curl -X POST "/charts" \
  -d '{"date": "1990-05-15T14:30:00Z", "latitude": 40.7128, "longitude": -74.0060}'
# Returns: {"chart_id": "chr_person1"}

curl -X POST "/charts" \
  -d '{"date": "1988-08-22T09:15:00Z", "latitude": 34.0522, "longitude": -118.2437}'
# Returns: {"chart_id": "chr_person2"}

# Step 2: Calculate synastry between the charts
curl -X POST "/charts/chr_person1/synastry" \
  -d '{
    "target_chart_id": "chr_person2",
    "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE"],
    "include_composite": true,
    "include_davison": true
  }'
```
**Benefits:**
- ✅ **Multi-chart operations** - synastry, composite charts
- ✅ **Complex analysis** - relationship dynamics
- ✅ **Stored for future** - revisit compatibility analysis
- ✅ **Advanced features** - composite and Davison charts

#### 📈 **Professional Astrologer Workflow**
```bash
# Step 1: Create client chart with detailed configuration
curl -X POST "/charts" \
  -d '{
    "date": "1985-12-03T16:45:00Z",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timezone": "Europe/Moscow",
    "config": {
      "house_system": "PLACIDUS",
      "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE", "SEXTILE", "QUINCUNX", "QUINTILE"],
      "orbs": {
        "conjunction": 10.0, "opposition": 10.0, "trine": 8.0,
        "square": 8.0, "sextile": 6.0, "quincunx": 3.0, "quintile": 2.0
      }
    }
  }'

# Step 2: Generate comprehensive natal analysis
curl -X POST "/charts/chr_client/positions" -d '{"include_speed": true}'
curl -X POST "/charts/chr_client/aspects" -d '{}'
curl -X POST "/charts/chr_client/houses" -d '{}'
curl -X POST "/charts/chr_client/dignities" -d '{"include_scores": true}'
curl -X POST "/charts/chr_client/arabic-parts" -d '{"parts": ["FORTUNA", "SPIRIT", "LOVE"]}'

# Step 3: Annual analysis for the coming year
curl -X POST "/charts/chr_client/progressions" \
  -d '{
    "target_date": "2024-12-03T16:45:00Z",
    "type": "SECONDARY",
    "include_returns": true,
    "include_angles": true
  }'

curl -X POST "/charts/chr_client/returns" \
  -d '{
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "types": ["SOLAR", "LUNAR"],
    "include_aspects": true
  }'

# Step 4: Check upcoming eclipses impact
curl -X POST "/charts/chr_client/eclipses" \
  -d '{
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "types": ["SOLAR", "LUNAR"],
    "include_aspects": true
  }'
```
**Benefits:**
- ✅ **Professional tools** - progressions, returns, eclipses
- ✅ **Client management** - store multiple client charts
- ✅ **Comprehensive analysis** - all calculations reference same chart
- ✅ **Time-based tracking** - annual patterns, life cycles

### Performance Comparison

| Feature | Direct Calculations | Chart-Based Calculations |
|---------|:------------------:|:------------------------:|
| **Speed** | ⚡ Fastest | 🚀 Fast (with caching) |
| **Database Usage** | None | Minimal reads |
| **House Information** | ❌ Not included | ✅ Always included |
| **User Preferences** | ❌ Manual each time | ✅ Stored and reused |
| **Complex Operations** | ❌ Limited | ✅ Full suite |
| **Caching Benefits** | ❌ No caching | ✅ Intelligent caching |
| **Authentication** | Required | Required |
| **Best For** | Real-time, widgets, APIs | Personal analysis, tracking |

### Choosing the Right Approach

#### Choose **Direct Calculations** when:
- Building real-time applications (current planetary positions)
- Creating public widgets or embeds
- Integrating with external systems
- Need maximum performance for simple calculations
- Don't need to track user preferences
- Building mobile apps with live sky data

#### Choose **Chart-Based Calculations** when:
- Building personal astrology applications
- Need to track individuals over time
- Performing complex multi-chart analysis (synastry)
- Want to store user preferences (house systems, orbs)
- Need house information for planets
- Building professional astrology tools
- Performing advanced calculations (progressions, returns)

### Hybrid Usage Patterns

Many applications benefit from using **both approaches**:

```bash
# Example: Astrology app with both features

# 1. Homepage widget - Direct calculation for current sky
curl -X POST "/calculations/planetary-positions" \
  -d '{"date": "2024-03-20", "time": "now", "latitude": user_lat, "longitude": user_lng}'

# 2. User's personal chart analysis - Chart-based
curl -X POST "/charts/user_chart_id/positions" -d '{}'
curl -X POST "/charts/user_chart_id/progressions" -d '{"target_date": "2024-03-20"}'
```

This hybrid approach gives you the **best of both worlds**: fast public features and powerful personal analysis tools.