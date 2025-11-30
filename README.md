# My Daily Tasks

A full-stack task management application with a React + Vite frontend and FastAPI backend.

## Project Structure

```
my-daily-tasks/
├── client/          # React + Vite frontend
├── server/          # FastAPI backend
└── openapi.yaml     # API specification
```

## Getting Started

### Prerequisites

- **Frontend**: Node.js 18+ and npm
- **Backend**: Python 3.13+ and [uv](https://github.com/astral-sh/uv)

### Running the Application

You can run both the frontend and backend with a single command from the root directory:

```bash
npm run dev
```

This will start:
- Backend at `http://localhost:3000`
- Frontend at `http://localhost:5173` (or next available port)

Alternatively, you can run them separately:

#### 1. Start the Backend Server

```bash
cd server
uv run uvicorn main:app --reload --port 3000
```

#### 2. Start the Frontend Client

```bash
cd client
npm run dev
```

### Running Tests

#### Backend Tests

```bash
cd server
uv run pytest test_api.py -v
```

All 27 integration tests should pass.

## Features

- ✅ **CRUD Operations**: Create, read, update, and delete todos  
- ✅ **Filtering**: Filter todos by due date and tags  
- ✅ **Modern UI**: Built with React, TypeScript, and Vite  
- ✅ **Type-Safe**: Full TypeScript support  
- ✅ **API Documentation**: Auto-generated with FastAPI  
- ✅ **Tested**: Comprehensive integration test suite  

## Configuration

### Frontend Environment Variables

Create `client/.env` to customize:

```env
VITE_API_URL=http://localhost:3000
```

### Backend Configuration

The backend runs on port 3000 by default. To change:

```bash
uv run uvicorn main:app --port 8000
```

Don't forget to update `VITE_API_URL` in the frontend if you change the port.

## API Endpoints

- `GET /api/todos` - Get all todos (supports `dueBefore` and `tags` filters)
- `POST /api/todos` - Create a new todo
- `PATCH /api/todos/{id}` - Update a todo
- `DELETE /api/todos/{id}` - Delete a todo
- `POST /api/todos/{id}/toggle` - Toggle completion status

See [openapi.yaml](openapi.yaml) for the complete API specification.

## Development

### Frontend

```bash
cd client
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

### Backend

```bash
cd server
uv run uvicorn main:app --reload  # Development with hot reload
uv run pytest test_api.py         # Run tests
```

## Architecture

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + Pydantic + Python 3.13
- **Data Storage**: In-memory (easily replaceable with database)
- **API Design**: RESTful, following OpenAPI 3.0 spec


## Documentation

- [Frontend README](client/README.md)
- [Backend README](server/README.md)
- [OpenAPI Specification](openapi.yaml)
