import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db

# Setup in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override dependency to use test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "todos_count" in data


class TestGetTodos:
    """Test GET /api/todos endpoint."""

    def test_get_empty_todos(self, client):
        """Test getting todos when database is empty."""
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_todos(self, client):
        """Test getting all todos."""
        # Create test todos
        todo1 = client.post(
            "/api/todos", json={"text": "Task 1", "tags": ["work"]}
        ).json()

        todo2 = client.post(
            "/api/todos", json={"text": "Task 2", "tags": ["personal"]}
        ).json()

        # Get all todos
        response = client.get("/api/todos")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        # Should be sorted by createdAt descending (newest first)
        assert todos[0]["id"] == todo2["id"]
        assert todos[1]["id"] == todo1["id"]

    def test_filter_by_due_date(self, client):
        """Test filtering todos by due date."""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        # Create todos with different due dates
        client.post(
            "/api/todos",
            json={
                "text": "Due today",
                "dueDate": today.isoformat(),
                "tags": ["urgent"],
            },
        )

        client.post(
            "/api/todos",
            json={
                "text": "Due next week",
                "dueDate": next_week.isoformat(),
                "tags": ["work"],
            },
        )

        client.post("/api/todos", json={"text": "No due date", "tags": ["personal"]})

        # Filter by tomorrow (should include today and no due date)
        response = client.get(f"/api/todos?dueBefore={tomorrow.isoformat()}")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        texts = [t["text"] for t in todos]
        assert "Due today" in texts
        assert "No due date" in texts
        assert "Due next week" not in texts

    def test_filter_by_single_tag(self, client):
        """Test filtering todos by a single tag."""
        client.post(
            "/api/todos", json={"text": "Work task", "tags": ["work", "important"]}
        )

        client.post("/api/todos", json={"text": "Personal task", "tags": ["personal"]})

        client.post("/api/todos", json={"text": "Another work task", "tags": ["work"]})

        # Filter by "work" tag
        response = client.get("/api/todos?tags=work")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        for todo in todos:
            assert "work" in todo["tags"]

    def test_filter_by_multiple_tags(self, client):
        """Test filtering todos by multiple tags (AND operation)."""
        client.post("/api/todos", json={"text": "Task 1", "tags": ["work", "urgent"]})

        client.post("/api/todos", json={"text": "Task 2", "tags": ["work"]})

        client.post("/api/todos", json={"text": "Task 3", "tags": ["urgent"]})

        # Filter by both "work" AND "urgent"
        response = client.get("/api/todos?tags=work,urgent")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["text"] == "Task 1"
        assert "work" in todos[0]["tags"]
        assert "urgent" in todos[0]["tags"]

    def test_filter_by_due_date_and_tags(self, client):
        """Test filtering by both due date and tags."""
        today = datetime.now()
        next_week = today + timedelta(days=7)

        client.post(
            "/api/todos",
            json={
                "text": "Work due soon",
                "dueDate": today.isoformat(),
                "tags": ["work"],
            },
        )

        client.post(
            "/api/todos",
            json={
                "text": "Personal due soon",
                "dueDate": today.isoformat(),
                "tags": ["personal"],
            },
        )

        client.post(
            "/api/todos",
            json={
                "text": "Work due later",
                "dueDate": next_week.isoformat(),
                "tags": ["work"],
            },
        )

        # Filter by due date and work tag
        tomorrow = today + timedelta(days=1)
        response = client.get(f"/api/todos?dueBefore={tomorrow.isoformat()}&tags=work")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["text"] == "Work due soon"

    def test_invalid_due_date_format(self, client):
        """Test that invalid due date format returns 400 error."""
        response = client.get("/api/todos?dueBefore=invalid-date")
        assert response.status_code == 400
        error = response.json()
        assert error["error"] == "VALIDATION_ERROR"
        assert "dueBefore" in error["details"]["field"]


class TestCreateTodo:
    """Test POST /api/todos endpoint."""

    def test_create_simple_todo(self, client):
        """Test creating a simple todo with only text."""
        response = client.post("/api/todos", json={"text": "Buy groceries"})
        assert response.status_code == 201
        todo = response.json()
        assert todo["text"] == "Buy groceries"
        assert todo["completed"] is False
        assert todo["tags"] == []
        assert todo["dueDate"] is None
        assert "id" in todo
        assert "createdAt" in todo

    def test_create_todo_with_all_fields(self, client):
        """Test creating a todo with all fields."""
        due_date = datetime(2025, 12, 1, 0, 0, 0)
        response = client.post(
            "/api/todos",
            json={
                "text": "Complete project",
                "tags": ["work", "urgent"],
                "dueDate": due_date.isoformat(),
            },
        )
        assert response.status_code == 201
        todo = response.json()
        assert todo["text"] == "Complete project"
        assert todo["tags"] == ["work", "urgent"]
        assert todo["dueDate"] is not None
        assert todo["completed"] is False

    def test_create_todo_without_text(self, client):
        """Test that creating todo without text returns validation error."""
        response = client.post("/api/todos", json={})
        assert response.status_code == 422  # Pydantic validation error

    def test_create_todo_with_empty_text(self, client):
        """Test that creating todo with empty text returns validation error."""
        response = client.post("/api/todos", json={"text": ""})
        assert response.status_code == 422


class TestUpdateTodo:
    """Test PATCH /api/todos/{id} endpoint."""

    def test_update_todo_text(self, client):
        """Test updating todo text."""
        # Create a todo
        todo = client.post("/api/todos", json={"text": "Original text"}).json()

        # Update text
        response = client.patch(
            f"/api/todos/{todo['id']}", json={"text": "Updated text"}
        )
        assert response.status_code == 200
        updated = response.json()
        assert updated["text"] == "Updated text"
        assert updated["id"] == todo["id"]

    def test_update_todo_completion(self, client):
        """Test updating todo completion status."""
        todo = client.post("/api/todos", json={"text": "Task to complete"}).json()

        response = client.patch(f"/api/todos/{todo['id']}", json={"completed": True})
        assert response.status_code == 200
        updated = response.json()
        assert updated["completed"] is True

    def test_update_todo_tags(self, client):
        """Test updating todo tags."""
        todo = client.post("/api/todos", json={"text": "Task", "tags": ["old"]}).json()

        response = client.patch(
            f"/api/todos/{todo['id']}", json={"tags": ["new", "updated"]}
        )
        assert response.status_code == 200
        updated = response.json()
        assert updated["tags"] == ["new", "updated"]

    def test_update_todo_due_date(self, client):
        """Test updating todo due date."""
        todo = client.post("/api/todos", json={"text": "Task"}).json()

        new_date = datetime(2025, 12, 31, 23, 59, 59)
        response = client.patch(
            f"/api/todos/{todo['id']}", json={"dueDate": new_date.isoformat()}
        )
        assert response.status_code == 200
        updated = response.json()
        assert updated["dueDate"] is not None

    def test_update_multiple_fields(self, client):
        """Test updating multiple fields at once."""
        todo = client.post("/api/todos", json={"text": "Original"}).json()

        response = client.patch(
            f"/api/todos/{todo['id']}",
            json={"text": "Updated", "completed": True, "tags": ["updated"]},
        )
        assert response.status_code == 200
        updated = response.json()
        assert updated["text"] == "Updated"
        assert updated["completed"] is True
        assert updated["tags"] == ["updated"]

    def test_update_nonexistent_todo(self, client):
        """Test updating a nonexistent todo returns 404."""
        response = client.patch("/api/todos/nonexistent", json={"text": "Updated"})
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "NOT_FOUND"

    def test_update_with_no_fields(self, client):
        """Test updating with no fields returns 400."""
        todo = client.post("/api/todos", json={"text": "Task"}).json()

        response = client.patch(f"/api/todos/{todo['id']}", json={})
        assert response.status_code == 400


class TestDeleteTodo:
    """Test DELETE /api/todos/{id} endpoint."""

    def test_delete_todo(self, client):
        """Test deleting a todo."""
        # Create a todo
        todo = client.post("/api/todos", json={"text": "To be deleted"}).json()

        # Delete it
        response = client.delete(f"/api/todos/{todo['id']}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get("/api/todos")
        assert len(get_response.json()) == 0

    def test_delete_nonexistent_todo(self, client):
        """Test deleting a nonexistent todo returns 404."""
        response = client.delete("/api/todos/nonexistent")
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "NOT_FOUND"


class TestToggleTodo:
    """Test POST /api/todos/{id}/toggle endpoint."""

    def test_toggle_incomplete_to_complete(self, client):
        """Test toggling incomplete todo to complete."""
        todo = client.post("/api/todos", json={"text": "Task to toggle"}).json()
        assert todo["completed"] is False

        response = client.post(f"/api/todos/{todo['id']}/toggle")
        assert response.status_code == 200
        toggled = response.json()
        assert toggled["completed"] is True

    def test_toggle_complete_to_incomplete(self, client):
        """Test toggling complete todo to incomplete."""
        # Create and mark as complete
        todo = client.post("/api/todos", json={"text": "Completed task"}).json()
        client.patch(f"/api/todos/{todo['id']}", json={"completed": True})

        # Toggle back to incomplete
        response = client.post(f"/api/todos/{todo['id']}/toggle")
        assert response.status_code == 200
        toggled = response.json()
        assert toggled["completed"] is False

    def test_toggle_multiple_times(self, client):
        """Test toggling a todo multiple times."""
        todo = client.post("/api/todos", json={"text": "Toggle test"}).json()

        # Toggle 1: incomplete -> complete
        response1 = client.post(f"/api/todos/{todo['id']}/toggle")
        assert response1.json()["completed"] is True

        # Toggle 2: complete -> incomplete
        response2 = client.post(f"/api/todos/{todo['id']}/toggle")
        assert response2.json()["completed"] is False

        # Toggle 3: incomplete -> complete
        response3 = client.post(f"/api/todos/{todo['id']}/toggle")
        assert response3.json()["completed"] is True

    def test_toggle_nonexistent_todo(self, client):
        """Test toggling a nonexistent todo returns 404."""
        response = client.post("/api/todos/nonexistent/toggle")
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "NOT_FOUND"


class TestIntegrationScenarios:
    """Test complete user scenarios."""

    def test_complete_todo_workflow(self, client):
        """Test a complete workflow: create, update, toggle, delete."""
        # Create
        todo = client.post(
            "/api/todos", json={"text": "Complete workflow test", "tags": ["test"]}
        ).json()
        assert todo["completed"] is False

        # Update tags
        updated = client.patch(
            f"/api/todos/{todo['id']}", json={"tags": ["test", "workflow"]}
        ).json()
        assert len(updated["tags"]) == 2

        # Toggle to complete
        completed = client.post(f"/api/todos/{todo['id']}/toggle").json()
        assert completed["completed"] is True

        # Delete
        response = client.delete(f"/api/todos/{todo['id']}")
        assert response.status_code == 204

        # Verify deleted
        all_todos = client.get("/api/todos").json()
        assert len(all_todos) == 0

    def test_filter_completed_vs_incomplete(self, client):
        """Test managing completed and incomplete todos."""
        # Create multiple todos
        for i in range(3):
            client.post("/api/todos", json={"text": f"Task {i + 1}", "tags": ["batch"]})

        # Get all
        all_todos = client.get("/api/todos").json()
        assert len(all_todos) == 3

        # Complete first two
        client.post(f"/api/todos/{all_todos[0]['id']}/toggle")
        client.post(f"/api/todos/{all_todos[1]['id']}/toggle")

        # Verify state
        current_todos = client.get("/api/todos").json()
        completed_count = sum(1 for t in current_todos if t["completed"])
        assert completed_count == 2
