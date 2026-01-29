# JustBackend

A secure, production-ready FastAPI backend application providing authenticated task management and URL shortening services with Supabase integration.

## Overview

JustBackend is a RESTful API built with FastAPI that offers:
1. **User Authentication** - Secure signup and login
2. **Task Management System** - Create, read, update, and delete tasks with user isolation
3. **URL Shortener** - Convert long URLs into shortened versions with user tracking

## Features

### 🔐 Authentication & Security
- JWT-based authentication with access tokens
- Secure signup and login
- Secure user isolation - users can only access their own data
- Row Level Security (RLS) policies in Supabase
- Protected API endpoints with Bearer token authentication

### ✅ Task Management API
- Create tasks with name, description, and completion status
- Retrieve all tasks (user-specific)
- Filter tasks by completion status
- Search tasks by ID
- Update existing tasks
- Delete tasks
- All operations are user-scoped for data privacy

### 🔗 URL Shortening Service
- Shorten URLs using TinyURL integration
- Store original and shortened URLs in database
- Retrieve all shortened URLs (user-specific)
- User-scoped URL tracking

### 🚀 Additional Features
- **Rate Limiting** - Protect against abuse
- **Input Validation** - Type-safe with Pydantic models
- **Error Handling** - Comprehensive error responses
- **CORS Support** - Ready for frontend integration
- **API Documentation** - Auto-generated Swagger/OpenAPI docs

## Project Structure

```
JustBackend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and route handlers
│   ├── auth.py           # Authentication routes and dependencies
│   ├── models.py         # Pydantic models for request validation
│   ├── databse.py        # Supabase client configuration
│   ├── limiter.py        # Rate limiting configuration
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
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

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
LIMIT=10/minute
```

4. Configure Supabase (see Database Setup below)

5. Run the application:
```bash
python main.py
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Database Setup

### 1. Create Tables

Run the following SQL in your Supabase SQL Editor:

```sql
-- Tasks Table
CREATE TABLE tasks (
  id BIGSERIAL PRIMARY KEY,
  task_name TEXT NOT NULL,
  task_description TEXT,
  done_status BOOLEAN DEFAULT FALSE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- URL Shortener Table
CREATE TABLE url_shortener (
  id BIGSERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  short_url TEXT NOT NULL,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_url_shortener_user_id ON url_shortener(user_id);
```

### 2. Enable Row Level Security (RLS)

```sql
-- Enable RLS on both tables
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE url_shortener ENABLE ROW LEVEL SECURITY;

-- Tasks Policies
CREATE POLICY "Users can view their own tasks"
ON tasks FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own tasks"
ON tasks FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own tasks"
ON tasks FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own tasks"
ON tasks FOR DELETE
USING (auth.uid() = user_id);

-- URL Shortener Policies
CREATE POLICY "Users can view their own URLs"
ON url_shortener FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own URLs"
ON url_shortener FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own URLs"
ON url_shortener FOR DELETE
USING (auth.uid() = user_id);
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register a new user | No |
| POST | `/auth/login` | Login and get access token | No |

### Task Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks/` | Get all user's tasks | Yes |
| POST | `/tasks/` | Create a new task | Yes |
| GET | `/tasks/status/{bool}` | Filter tasks by completion status | Yes |
| GET | `/tasks/{task_id}` | Get a specific task by ID | Yes |
| PUT | `/tasks/{task_id}` | Update a task | Yes |
| DELETE | `/tasks/{task_id}` | Delete a task | Yes |

### URL Shortener

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/url-shortener` | Shorten a URL | Yes |
| GET | `/url-shortener/` | Get all user's shortened URLs | Yes |

### Health & Info

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Welcome message | No |
| GET | `/health` | Health check | No |

## Example Usage

### 1. Sign Up
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "message": "User signed up successfully",
  "user_id": "abc-123-def",
  "email": "user@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "message": "User logged in successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "abc-123-def",
  "token_type": "bearer"
}
```

### 3. Create a Task (Authenticated)
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "task_name": "Buy groceries",
    "task_description": "Milk, eggs, bread",
    "done_status": false
  }'
```

### 4. Get All Tasks (Authenticated)
```bash
curl -X GET "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Update a Task (Authenticated)
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "task_name": "Buy groceries",
    "task_description": "Milk, eggs, bread, cheese",
    "done_status": true
  }'
```

### 6. Shorten a URL (Authenticated)
```bash
curl -X POST "http://localhost:8000/url-shortener" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "url": "https://www.example.com/very/long/url/path"
  }'
```

**Response:**
```json
{
  "original_url": "https://www.example.com/very/long/url/path",
  "short_url": "https://tinyurl.com/abc123",
  "created_at": "2026-01-29T10:30:00"
}
```

## Dependencies

- **FastAPI** - Modern, fast web framework for building APIs
- **Supabase** - Backend-as-a-Service for database and authentication
- **Pyshorteners** - URL shortening library (TinyURL integration)
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running FastAPI
- **python-dotenv** - Environment variable management
- **slowapi** - Rate limiting for FastAPI

## Security Best Practices

1. **JWT Tokens**: All authenticated endpoints require Bearer token
2. **User Isolation**: Users can only access their own data
3. **Row Level Security**: Database-level access control via Supabase RLS
4. **Password Security**: Handled by Supabase authentication
5. **Rate Limiting**: Prevents API abuse
6. **CORS**: Configurable for your frontend domain
7. **Environment Variables**: Sensitive data stored in `.env` file

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

Example error response:
```json
{
  "detail": "Invalid authentication credentials"
}
```

## Development

### Run with Auto-Reload
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing Authentication Flow
1. Signup → Get access_token
2. Login → Get access_token  
3. Use access_token in Authorization header for protected endpoints

## Deployment

### Environment Variables for Production
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
LIMIT=100/minute
```

### Production Checklist
- [ ] Set appropriate rate limits
- [ ] Configure CORS for your frontend domain
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure proper RLS policies

## License

This project is proprietary and confidential.

## Contributing

This is a private project. For questions or contributions, please contact the maintainer.

## Changelog

### Version 2.0.0 (Current)
- ✅ Added user authentication (signup, login)
- ✅ User isolation for tasks and URLs
- ✅ Row Level Security (RLS) policies
- ✅ JWT-based authentication
- ✅ Rate limiting
- ✅ Improved error handling
- ✅ Security enhancements
- ✅ Changed task identification from name to ID
- ✅ Added user_id foreign keys with CASCADE delete

### Version 1.0.0
- ✅ Basic task management
- ✅ URL shortening service
- ✅ Supabase integration

## Future Enhancements

- [ ] Email verification for new users
- [ ] Password reset functionality
- [ ] Logout endpoint
- [ ] Refresh token rotation
- [ ] OAuth providers (Google, GitHub)
- [ ] Task pagination with cursor-based navigation
- [ ] Task categories and tags
- [ ] Task due dates and reminders
- [ ] Custom short URL aliases
- [ ] URL analytics and click tracking
- [ ] Task sharing between users
- [ ] Export tasks to CSV/JSON
- [ ] WebSocket support for real-time updates
- [ ] File attachments for tasks
- [ ] Task search and filtering
- [ ] API versioning

## Support

For issues, questions, or feature requests, please contact the development team.

---

**Built with ❤️ using FastAPI and Supabase**
