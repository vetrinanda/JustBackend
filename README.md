# JustBackend

A secure, production-ready FastAPI backend application providing authenticated task management, URL shortening services, and AI-powered video analysis.

## Overview

JustBackend is a RESTful API built with FastAPI that offers:
1. **User Authentication** - Secure signup, login, and SMS OTP verification.
2. **Task Management System** - Create, read, update, and delete tasks with user isolation and caching.
3. **URL Shortener** - Convert long URLs into shortened versions with user tracking.
4. **AI Video Analysis** - Analyze videos using Google Gemini models via Pydantic AI.
5. **Performance** - Redis caching for optimized data retrieval.

## Features

### 🔐 Authentication & Security
- **JWT-based authentication** with access/refresh tokens.
- **Secure Signup & Login** (Email/Password).
- **OTP Authentication**: SMS-based One-Time Password verification.
- **Sign Out**: Securely terminate user sessions.
- **User Isolation**: Users can only access their own data.
- **Row Level Security (RLS)** policies in Supabase.

### 🤖 AI Capabilities
- **Video Analysis**: Ask questions about video content using the `/video` endpoint.
- **Powered by**: Pydantic AI and Google Gemini Models.

### ✅ Task Management API
- Create tasks with name, description, and completion status.
- Retrieve all tasks (user-specific) with **Redis Caching**.
- Filter tasks by completion status.
- Search tasks by ID.
- Update existing tasks.
- Delete tasks.

### 🔗 URL Shortening Service
- Shorten URLs using TinyURL integration.
- Store original and shortened URLs in database.
- Retrieve all shortened URLs (user-specific) with **Redis Caching**.
- User-scoped URL tracking.

### 🚀 Additional Features
- **Rate Limiting** - Protect against abuse (using `slowapi`).
- **Input Validation** - Type-safe with Pydantic models.
- **Docker Ready**.
- **CORS Support** - Configured for cross-origin requests.

## Project Structure

```
JustBackend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Main FastAPI application and route definitions
│   ├── auth.py           # Authentication routes (Signup, Login, OTP, Signout)
│   ├── agent.py          # AI Agent routes (Video Analysis)
│   ├── models.py         # Pydantic models
│   ├── databse.py        # Supabase client configuration
│   ├── limiter.py        # Rate limiting setup
├── main.py               # Application entry point (Uvicorn runner)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── pyproject.toml        # Project configuration & Dependencies
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.13+**
- **Supabase** account and project.
- **Redis** server running locally (default: `localhost:6379`).
- **Google API Key** (for Gemini AI).
- `uv` or `pip` package manager.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd JustBackend
   ```

2. **Install dependencies:**
   Using `uv` (recommended):
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis Server:**
   Ensure you have a Redis instance running locally on port `6379`.
   ```bash
   # Example with Docker
   docker run -d -p 6379:6379 redis
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your-project-url
   SUPABASE_KEY=your-anon-key
   API_KEY=your-google-api-key
   LIMIT=10/minute
   ```

5. **Run the Application:**
   ```bash
   python main.py
   # or
   uvicorn app.main:app --reload
   ```

## Database Setup

Run the following SQL in your Supabase SQL Editor.

### 1. Create Tables

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

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_url_shortener_user_id ON url_shortener(user_id);
```

### 2. Enable Row Level Security (RLS)

```sql
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE url_shortener ENABLE ROW LEVEL SECURITY;

-- Policies for Tasks
CREATE POLICY "Users can view their own tasks" ON tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own tasks" ON tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own tasks" ON tasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own tasks" ON tasks FOR DELETE USING (auth.uid() = user_id);

-- Policies for URL Shortener
CREATE POLICY "Users can view their own URLs" ON url_shortener FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own URLs" ON url_shortener FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own URLs" ON url_shortener FOR DELETE USING (auth.uid() = user_id);
```

## API Endpoints

### AI Agent
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/video` | Analyze a video with AI | No (Currently) |

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register a new user | No |
| POST | `/auth/login` | Login (Email/Password) | No |
| POST | `/auth/send-otp` | Send SMS OTP to phone | No |
| POST | `/auth/verify-otp` | Verify SMS OTP & Login | No |
| POST | `/auth/signout` | Sign out current user | Yes |

### Task Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks/` | Get all user's tasks (Cached) | Yes |
| POST | `/tasks/` | Create a new task | Yes |
| GET | `/tasks/status/{bool}` | Filter by completion status | Yes |
| GET | `/tasks/{task_id}` | Get a specific task by ID | Yes |
| PUT | `/tasks/{task_id}` | Update a task | Yes |
| DELETE | `/tasks/{task_id}` | Delete a task | Yes |

### URL Shortener
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/url-shortener` | Shorten a URL | Yes |
| GET | `/url-shortener/` | Get all user's URLs (Cached) | Yes |

## Example Usage

### 1. Analyze Video (AI)
```bash
curl -X POST "http://localhost:8000/video" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "question": "Describe the events in this video."
  }'
```

### 2. Send OTP (SMS)
```bash
curl -X POST "http://localhost:8000/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{ "phone": "+1234567890" }'
```

---

**Built with ❤️ using FastAPI, Supabase, Redis, and Pydantic AI**
