from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Todo(BaseModel):
    """Todo model matching the OpenAPI specification."""

    model_config = ConfigDict(
        # Allow datetime to be serialized as ISO 8601 strings
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    id: str
    text: str = Field(..., min_length=1, max_length=500)
    completed: bool
    dueDate: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    createdAt: datetime


class CreateTodoRequest(BaseModel):
    """Request model for creating a new todo."""

    text: str = Field(..., min_length=1, max_length=500)
    dueDate: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)


class UpdateTodoRequest(BaseModel):
    """Request model for updating an existing todo. All fields are optional."""

    model_config = ConfigDict(extra="forbid")

    text: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None
    dueDate: Optional[datetime] = None
    tags: Optional[list[str]] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    message: str
    details: Optional[dict] = None
