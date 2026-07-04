# App Directory Structure

This directory contains the reorganized backend code following best practices for scalability.

## Structure

```
app/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI app initialization and middleware
├── models.py                # Pydantic models for request/response validation
├── api/
│   ├── __init__.py
│   └── routes.py            # API route handlers
├── core/
│   ├── __init__.py
│   └── config.py            # Configuration management
└── services/
    ├── __init__.py
    └── calculator.py        # Business logic (calculations)
```

## Files Description

### `main.py`
- FastAPI application initialization
- CORS middleware configuration
- Router inclusion
- Startup/shutdown events

### `models.py`
- Pydantic models for request/response validation
- `CatRequest`: Request model for calorie calculation
- `WeightConversionRequest`: Request model for weight conversion
- `WeightConversionResponse`: Response model for weight conversion
- `CalorieResponse`: Response model for calorie calculation

### `api/routes.py`
- All API endpoint handlers
- Route definitions using APIRouter
- Request validation and error handling

### `core/config.py`
- Configuration management
- Settings class that loads from config.json
- Application-wide settings (CORS, API metadata, etc.)

### `services/calculator.py`
- Business logic for calculations
- Weight conversion functions
- Calorie calculation functions
- Pure functions (no side effects)

## Benefits of This Structure

1. **Separation of Concerns**: Each file has a clear, single responsibility
2. **Scalability**: Easy to add new routes, models, or services
3. **Testability**: Services can be tested independently
4. **Database Ready**: Easy to add database models and operations
5. **Maintainability**: Clear structure makes code easier to understand and modify

## Future Additions

When adding a database, you would create:

```
app/
├── db/
│   ├── __init__.py
│   ├── database.py          # Database connection
│   └── models.py            # SQLAlchemy/ORM models
├── crud/
│   ├── __init__.py
│   └── cat.py               # CRUD operations for cats
└── schemas/                 # Rename current models.py to schemas.py
    └── ...
```

This structure scales well for features like:
- User authentication
- Data persistence
- Background tasks
- Multiple API versions
- Admin interfaces
