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

### Calculations

#### Planetary Positions

```http
POST /charts/{chart_id}/positions
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
    "include_retrograde": true,
    "include_speed": true
}
```

Response:

```json
{
    "success": true,
    "data": {
        "positions": {
            "SUN": {
                "longitude": 359.5,
                "latitude": 0.0,
                "distance": 0.983,
                "declination": -0.5,
                "speed": 0.985,
                "is_retrograde": false
            },
            "MOON": {
                "longitude": 45.2,
                "latitude": 2.3,
                "distance": 0.0025,
                "declination": 15.8,
                "speed": 13.2,
                "is_retrograde": false
            }
        }
    }
}
```

#### Aspects

```http
POST /charts/{chart_id}/aspects
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
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
                "angle": 45.7,
                "orb": 0.7,
                "aspect_type": "CONJUNCTION",
                "applying": true
            }
        ]
    }
}
```

#### Houses

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
        "houses": {
            "ASC": 45.2,
            "MC": 135.8,
            "DESC": 225.2,
            "IC": 315.8,
            "HOUSE_1": 45.2,
            "HOUSE_2": 75.3,
            "HOUSE_3": 105.4
        }
    }
}
```

#### Fixed Stars

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

#### Arabic Parts

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

#### Dignities

```http
POST /charts/{chart_id}/dignities
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
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

#### Antiscia

```http
POST /charts/{chart_id}/antiscia
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
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

#### Declinations

```http
POST /charts/{chart_id}/declinations
```

Request:

```json
{
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
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

#### Harmonics

```http
POST /charts/{chart_id}/harmonics
```

Request:

```json
{
    "harmonic": 2,
    "planets": ["SUN", "MOON", "MARS", "VENUS"],
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

#### Rectification

```http
POST /charts/{chart_id}/rectify
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

### Advanced Calculations

#### Synastry

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

#### Progressions

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

#### Directions

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

#### Returns

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

#### Eclipses

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

#### Ingresses

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

## Rate Limits

- Free tier: 100 requests per hour
- Basic tier: 1,000 requests per hour
- Pro tier: 10,000 requests per hour
- Enterprise tier: Custom limits

## Error Codes

- `VALIDATION_ERROR`: Invalid input parameters
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## WebSocket API

### Connection

```
wss://api.nocturna-calculations.com/v1/ws
```

### Authentication

Send authentication message after connection:

```json
{
    "type": "auth",
    "token": "your_jwt_token"
}
```

### Real-time Calculations

Subscribe to calculation updates:

```json
{
    "type": "subscribe",
    "chart_id": "chr_123456",
    "calculations": ["positions", "aspects"]
}
```

### Calculation Updates

```json
{
    "type": "update",
    "chart_id": "chr_123456",
    "calculation": "positions",
    "data": {
        "SUN": {
            "longitude": 45.2,
            "latitude": 0.0
        }
    }
}
```