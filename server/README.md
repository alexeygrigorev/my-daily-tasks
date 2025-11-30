# My Daily Tasks API Server

FastAPI backend for the My Daily Tasks application.

## Features

- ✅ Full CRUD operations for todos
- ✅ Filter todos by due date and tags
- ✅ CORS enabled for frontend integration
- ✅ In-memory data store (easy to replace with database)
- ✅ OpenAPI/Swagger documentation
- ✅ Validation and error handling

## Setup

### Install Dependencies

```bash
uv add fastapi uvicorn[standard] python-dateutil
```

Or if dependencies are already in `pyproject.toml`:

```bash
uv sync
```

## Running the Server

### Development Mode (with auto-reload)

```bash
uv run uvicorn main:app --reload --port 3000
```

The API will be available at `http://localhost:3000`

### Production Mode

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 3000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
- **OpenAPI JSON**: http://localhost:3000/openapi.json

## API Endpoints

### GET /api/todos

Get all todos with optional filtering.

**Query Parameters:**
- `dueBefore` (optional): ISO 8601 date-time string - filter todos due on or before this date
- `tags` (optional): Comma-separated tags - filter todos that have ALL specified tags

**Examples:**

```bash
# Get all todos
curl http://localhost:3000/api/todos

# Get todos due today or earlier
curl "http://localhost:3000/api/todos?dueBefore=2025-11-30T23:59:59.999Z"

# Get todos tagged with "work"
curl "http://localhost:3000/api/todos?tags=work"

# Get work todos due within a week
curl "http://localhost:3000/api/todos?dueBefore=2025-12-07T23:59:59.999Z&tags=work"

# Get todos with multiple tags (must have ALL tags)
curl "http://localhost:3000/api/todos?tags=work,urgent"
```

### POST /api/todos

Create a new todo.

```bash
curl -X POST http://localhost:3000/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Complete project documentation",
    "tags": ["work", "documentation"],
    "dueDate": "2025-12-01T00:00:00Z"
  }'
```

### PATCH /api/todos/{id}

Update an existing todo (all fields optional).

```bash
# Mark as completed
curl -X PATCH http://localhost:3000/api/todos/{id} \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Update text and tags
curl -X PATCH http://localhost:3000/api/todos/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Updated task description",
    "tags": ["work", "updated"]
  }'
```

### DELETE /api/todos/{id}

Delete a todo.

```bash
curl -X DELETE http://localhost:3000/api/todos/{id}
```

### POST /api/todos/{id}/toggle

Toggle the completion status of a todo.

```bash
curl -X POST http://localhost:3000/api/todos/{id}/toggle
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:3000/health
# Response: {"status": "ok", "todos_count": 0}
```

## Data Models

### Todo

```json
{
  "id": "string",
  "text": "string (1-500 chars)",
  "completed": false,
  "dueDate": "2025-12-01T00:00:00Z",  // ISO 8601, optional
  "tags": ["work", "urgent"],
  "createdAt": "2025-11-30T10:00:00Z"
}
```

## CORS Configuration

The server allows requests from these origins:
- `http://localhost:5173` (Vite default)
- `http://localhost:5174`
- `http://localhost:3000`
- `http://localhost:4173` (Vite preview)

To add more origins, edit the `allow_origins` list in `main.py`.

## Error Responses

The API returns consistent error responses:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "fieldName",
    "reason": "Detailed reason"
  }
}
```

**Error Codes:**
- `404 NOT_FOUND` - Todo not found
- `400 VALIDATION_ERROR` - Invalid request parameters
- `422 Unprocessable Entity` - Validation errors (automatic from Pydantic)
- `500 INTERNAL_SERVER_ERROR` - Unexpected errors

## Project Structure

```
server/
├── main.py          # FastAPI application and endpoints
├── models.py        # Pydantic models
├── pyproject.toml   # Dependencies (managed by uv)
└── README.md        # This file
```

## Next Steps

### Database Integration

To add persistent storage, replace the in-memory `todos_db` with a database:

1. **SQLite** (simplest):
   ```bash
   uv add sqlmodel  # or sqlalchemy
   ```

2. **PostgreSQL**:
   ```bash
   uv add psycopg2-binary sqlalchemy
   ```

3. Update `main.py` to use database queries instead of dict operations

### Authentication

To add authentication:

```bash
uv add python-jose[cryptography] passlib[bcrypt]
```

Then add security schemes to the OpenAPI spec and implement JWT tokens.

### Deployment

Deploy to:
- **Railway**: `railway up`
- **Fly.io**: `fly launch`
- **Docker**: Create a Dockerfile with `FROM python:3.13` and `uv` installation
- **Vercel/Netlify**: Use serverless functions

## Testing

Test the API using:
- **curl** (examples above)
- **Postman** (import the OpenAPI spec)
- **Swagger UI** (http://localhost:3000/docs)
- **httpie**: `http :3000/api/todos`

## Development

Hot reload is enabled by default with the `--reload` flag:

```bash
uv run uvicorn main:app --reload --port 3000
```

Changes to `main.py` or `models.py` will automatically restart the server.

## Seeding Database with Fake Data

To populate the database with 100 fake todo records for testing:

```bash
uv run python seed_data.py
```

This script will:
- Generate 100 realistic todo items
- Use tags: `personal`, `groceries`, `course`, `work`
- Create due dates anchored to today (ranging from 30 days past to 30 days future)
- Randomly mark ~20% as completed
- Display statistics after insertion

The fake data includes realistic task descriptions appropriate to each tag category and helps test filtering, sorting, and pagination features.
