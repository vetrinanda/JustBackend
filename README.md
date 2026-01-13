```markdown
# JustBackend

A FastAPI-based backend application providing task management and URL shortening services with Supabase integration.

## Overview

JustBackend is a RESTful API built with FastAPI that offers two main functionalities:
1. **Task Management System** - Create, read, update, and delete tasks with status tracking
2. **URL Shortener** - Convert long URLs into shortened versions using TinyURL

## Features

- **Task Management API**
  - Create tasks with name, description, and completion status
  - Retrieve all tasks or filter by completion status
  - Search tasks by name
  - Update existing tasks
  - Delete tasks

- **URL Shortening Service**
  - Shorten URLs using TinyURL integration
  - Store original and shortened URLs in database

- **Supabase Integration** - Cloud database with real-time capabilities
- **RESTful Design** - Clean and intuitive API endpoints
- **Pydantic Models** - Type validation and data modeling
- **Production Ready** - Built with FastAPI for high performance

## Project Structure

```
JustBackend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and route handlers
│   ├── models.py         # Pydantic models for request validation
│   ├── databse.py        # Supabase client configuration
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd JustBackend
```

2. Install dependencies:
```bash
uv sync
# or
pip install -r requirements.txt
```

3. Configure Supabase:
   - Create a Supabase project
   - Set up your Supabase URL and API key in `app/databse.py`
   - Create the required tables (see Database Setup below)

4. Run the application:
```bash
python main.py
# or
uvicorn app.main:app --reload
```

## Database Setup

Create the following tables in your Supabase database:

### Tasks Table
```sql
CREATE TABLE tasks (
  id BIGSERIAL PRIMARY KEY,
  task_name TEXT NOT NULL,
  task_description TEXT,
  done_status BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### URL Shortener Table
```sql
CREATE TABLE url_shortner (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  short_url TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Row Level Security (RLS) Policies
```sql
-- Enable RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE url_shortner ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Allow public access" ON tasks FOR ALL TO public USING (true);
CREATE POLICY "Allow public access" ON url_shortner FOR ALL TO public USING (true);
```

## API Endpoints

### Task Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/tasks/` | Get all tasks |
| POST | `/tasks/` | Create a new task |
| GET | `/tasks/done_status?task_status={bool}` | Filter tasks by completion status |
| GET | `/tasks/{task_name}` | Get a specific task by name |
| PUT | `/tasks/{task_name}` | Update a task |
| DELETE | `/tasks/{task_name}` | Delete a task |

### URL Shortener

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/url-shortner?url={url}` | Shorten a URL |

## Example Usage

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Buy groceries",
    "task_description": "Milk, eggs, bread",
    "done_status": false
  }'
```

### Shorten a URL
```bash
curl -X POST "http://localhost:8000/url-shortner?url=https://www.example.com/very/long/url"
```

## Dependencies

- **FastAPI** - Modern web framework for building APIs
- **Supabase** - Backend-as-a-Service for database and authentication
- **Pyshorteners** - URL shortening library
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running FastAPI

## Configuration

Update your Supabase credentials in `app/databse.py`:

```python
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"  # or service-role-key
```

## Development

To run in development mode with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## License

This project is proprietary and confidential.

## Future Enhancements

- [ ] Add user authentication
- [ ] Implement pagination for task lists
- [ ] Add custom short URL aliases
- [ ] URL analytics and click tracking
- [ ] Task categories and tags
- [ ] Due dates and reminders

```