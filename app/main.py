from functools import cache
import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import pyshorteners
import json
import redis

rd=redis.Redis(host='localhost', port=6379, db=0)

load_dotenv()

from app.databse import supabase  # Note: typo 'databse' should be 'database'
from app.models import TaskCreate
from app.limiter import limiter
from app.auth import user_dependency, get_current_user, router
from app import agent

app = FastAPI(
    title="Task Management API",
    description="API for managing tasks URL shortening, and Youtube video question answering.",
    version="1.0.0"
)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(router)
app.include_router(agent.router)

# Get rate limit from environment
limit = os.getenv("LIMIT", "10/minute")  # Default fallback


# Pydantic model for URL shortener
class UrlShortenerRequest(BaseModel):
    url: HttpUrl  # Validates URL format
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.example.com/very/long/url"
            }
        }


@app.get("/")
def read_root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to the Task Management API,URL shortener,and Youtube video question answering service.",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")  # Changed from POST to GET
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        supabase.table("tasks").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


@app.get("/tasks/", response_model=list)
@limiter.limit(limit)
def read_tasks(request: Request, current_user: user_dependency):
    """Get all tasks for the current user"""
    cache=rd.get(f"tasks_{current_user['user_id']}")
    if cache:
        return json.loads(cache)
    else:
        try:
            response = (
                supabase.table("tasks")
                .select("*")
                .eq("user_id", current_user["user_id"])  # Filter by user
                .execute()
            )
            rd.set(f"tasks_{current_user['user_id']}", json.dumps(response.data), ex=120)  # Cache for 120 seconds
            return response.data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch tasks: {str(e)}"
            )


@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
@limiter.limit(limit)
def create_task(
    request: Request,
    task: TaskCreate,
    current_user: user_dependency
):
    """Create a new task"""
    try:
        response = (
            supabase.table("tasks")
            .insert({
                "task_name": task.task_name,
                "task_description": task.task_description,
                "done_status": task.done_status,
                "user_id": current_user["user_id"]  # Associate with user
            })
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task creation failed"
            )
        
        return {
            "message": "Task added successfully",
            "task": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@app.get("/tasks/status/{task_status}")  # Better path structure
@limiter.limit(limit)
def get_tasks_by_status(
    request: Request,
    task_status: bool,
    current_user: user_dependency
):
    """Get tasks filtered by completion status"""
    try:
        response = (
            supabase.table("tasks")
            .select("*")
            .eq("done_status", task_status)
            .eq("user_id", current_user["user_id"])  # Filter by user
            .execute()
        )
        return {"tasks": response.data, "count": len(response.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@app.get("/tasks/{task_id}")  # Use task_id instead of task_name for unique identification
@limiter.limit(limit)
def read_task(
    request: Request,
    task_id: int,
    current_user: user_dependency
):
    """Get a specific task by ID"""
    try:
        response = (
            supabase.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("user_id", current_user["user_id"])  # Ensure user owns the task
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        return {"task": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )


@app.put("/tasks/{task_id}")
@limiter.limit(limit)
def update_task(
    request: Request,
    task_id: int,
    task: TaskCreate,
    current_user: user_dependency
):
    """Update an existing task"""
    try:
        # First check if task exists and belongs to user
        existing = (
            supabase.table("tasks")
            .select("id")
            .eq("id", task_id)
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        response = (
            supabase.table("tasks")
            .update({
                "task_name": task.task_name,
                "task_description": task.task_description,
                "done_status": task.done_status
            })
            .eq("id", task_id)
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        
        return {
            "message": "Task updated successfully",
            "task": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(limit)
def delete_task(
    request: Request,
    task_id: int,
    current_user: user_dependency
):
    """Delete a task"""
    try:
        # Check if task exists and belongs to user
        existing = (
            supabase.table("tasks")
            .select("id")
            .eq("id", task_id)
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        supabase.table("tasks").delete().eq("id", task_id).execute()
        
        return  # 204 No Content - no body returned
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@app.post("/url-shortener", status_code=status.HTTP_201_CREATED)  # Fixed typo: shortner -> shortener
@limiter.limit(limit)
def shorten_url(
    request: Request,
    url_request: UrlShortenerRequest,
    current_user: user_dependency
):
    """Shorten a URL"""
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(str(url_request.url))
        
        response = (
            supabase.table("url_shortener")  # Fixed table name typo
            .insert({
                "url": str(url_request.url),
                "short_url": short_url,
                "user_id": current_user["user_id"]  # Associate with user
            })
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL shortening failed"
            )
        
        inserted_data = response.data[0]
        return {
            "original_url": inserted_data["url"],
            "short_url": inserted_data["short_url"],
            "created_at": inserted_data.get("created_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to shorten URL: {str(e)}"
        )


@app.get("/url-shortener/", response_model=list)
@limiter.limit(limit)
def get_shortened_urls(request: Request, current_user: user_dependency):
    """Get all shortened URLs for the current user"""
    cache=rd.get(f"url_shortener_{current_user['user_id']}")
    if cache:
        return json.loads(cache)
    try:
        response = (
            supabase.table("url_shortener")
            .select("*")
            .eq("user_id", current_user["user_id"])
            .execute()
        )
        rd.set(f"url_shortener_{current_user['user_id']}", json.dumps(response.data), ex=120)  # Cache for 120 seconds
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch URLs: {str(e)}"
        )