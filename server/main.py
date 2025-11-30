from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dateutil import parser
import time

from models import Todo, CreateTodoRequest, UpdateTodoRequest, ErrorResponse

app = FastAPI(
    title="My Daily Tasks API",
    description="RESTful API for managing daily tasks",
    version="1.0.0",
)

# CORS middleware - allow requests from frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:4173",  # Vite preview
        "http://localhost:8080",  # Previous frontend port
        "http://localhost:8081",  # Current frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data store
todos_db: dict[str, Todo] = {}
id_counter = 0


def generate_id() -> str:
    """Generate a unique ID for a new todo."""
    global id_counter
    id_counter += 1
    return f"{int(time.time() * 1000)}{id_counter}"


@app.get("/api/todos", response_model=list[Todo])
async def get_todos(
    dueBefore: Optional[str] = Query(
        None, description="Filter todos with due date on or before this date"
    ),
    tags: Optional[str] = Query(
        None, description="Comma-separated list of tags to filter by"
    ),
) -> list[Todo]:
    """
    Get all todos with optional filtering.

    - **dueBefore**: Returns todos where dueDate <= dueBefore (inclusive). Also includes todos without a due date.
    - **tags**: Returns todos that have ALL specified tags (AND operation). Case-sensitive.
    """
    result = list(todos_db.values())

    # Filter by due date
    if dueBefore:
        try:
            due_before_dt = parser.isoparse(dueBefore)
            result = [
                todo
                for todo in result
                if todo.dueDate is None or todo.dueDate <= due_before_dt
            ]
        except (ValueError, parser.ParserError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid query parameters",
                    "details": {
                        "field": "dueBefore",
                        "reason": "Invalid date format. Expected ISO 8601 format.",
                    },
                },
            )

    # Filter by tags (AND operation - todo must have all specified tags)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        result = [todo for todo in result if all(tag in todo.tags for tag in tag_list)]

    # Sort by createdAt descending (newest first)
    result.sort(key=lambda x: x.createdAt, reverse=True)

    return result


@app.post("/api/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(request: CreateTodoRequest) -> Todo:
    """Create a new todo item."""
    new_todo = Todo(
        id=generate_id(),
        text=request.text,
        completed=False,
        dueDate=request.dueDate,
        tags=request.tags,
        createdAt=datetime.now(),
    )

    todos_db[new_todo.id] = new_todo
    return new_todo


@app.patch("/api/todos/{id}", response_model=Todo)
async def update_todo(id: str, request: UpdateTodoRequest) -> Todo:
    """Update an existing todo."""
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Todo not found"},
        )

    todo = todos_db[id]

    # Update only the fields that are provided
    update_data = request.model_dump(exclude_unset=True)

    # Check if at least one field is being updated
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "At least one field must be provided for update",
            },
        )

    for field, value in update_data.items():
        setattr(todo, field, value)

    return todo


@app.delete("/api/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(id: str):
    """Delete a todo item."""
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Todo not found"},
        )

    del todos_db[id]
    return None


@app.post("/api/todos/{id}/toggle", response_model=Todo)
async def toggle_todo(id: str) -> Todo:
    """Toggle the completion status of a todo."""
    if id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Todo not found"},
        )

    todo = todos_db[id]
    todo.completed = not todo.completed

    return todo


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom exception handler to format errors consistently."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP_ERROR", "message": exc.detail},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "todos_count": len(todos_db)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
