import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import Request
from pydantic import BaseModel
from dotenv import load_dotenv
from app.databse import supabase
from app.models import TaskCreate
# from sqlalchemy.orm import Session
import pyshorteners
from app.limiter import limiter

app = FastAPI()

# Create the database tables
# TTask.metadata.create_all(bind=engine)
# Url.metadata.create_all(bind=engine)

limit = os.getenv("LIMIT")

class SignupData(BaseModel):
    email: str
    password: str


# Authentication dependency
def get_current_user(request: Request):
    """Verify the user is authenticated by checking the authorization header"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token from "Bearer <token>"
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
        
# db: Session = Depends(get_db)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management API"}

app.post("/health")
def health_check():
    return {"status": "API is healthy"}

@app.post("/signup")
def signup(sign: SignupData):
    try:
        response = supabase.auth.sign_up(
            {"email": sign.email,
             "password": sign.password}
        )
        return {
            "message": "User signed up successfully",
            "access_token": response.session.access_token if response.session else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/login")
def login(sign: SignupData):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": sign.email,
             "password": sign.password}
        )
        return {
            "message": "User logged in successfully",
            "access_token": response.session.access_token,
            "user_id": response.user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@app.get("/tasks/")
@limiter.limit(limit)
def read_tasks(request: Request, current_user = Depends(get_current_user)):
    response = (
    supabase.table("tasks")
    .select("*")
    .execute()
)
    return response.data

@app.post("/tasks/")
@limiter.limit(limit)
def create_task(request: Request, task: TaskCreate, current_user = Depends(get_current_user)):
    response = (
    supabase.table("tasks")
    .insert({"task_name": task.task_name,
             "task_description": task.task_description,
             "done_status": task.done_status})
    .execute())
    return {"Task Added Sucessfully": response.data}

@app.get("/tasks/done_status")
@limiter.limit(limit)
def get_task_status(request: Request, task_status: bool, current_user = Depends(get_current_user)):
    response = (
    supabase.table("tasks")
    .select("*")
    .eq("done_status",task_status)
    .execute())
    return {"Response": response.data}


@app.get("/tasks/{task_name}")
@limiter.limit(limit)
def read_task(request: Request, task_name: str, current_user = Depends(get_current_user)):
    response=(supabase.table("tasks")
              .select("*")
              .eq("task_name",task_name)
              .execute())
    return {"Reponse":response.data}

@app.put("/tasks/{task_name}")
@limiter.limit(limit)
def update_task(request: Request, task_name: str, task: TaskCreate, current_user = Depends(get_current_user)):
    response = (
    supabase.table("tasks")
    .update({"task_name": task.task_name,
             "task_description": task.task_description,
             "done_status": task.done_status})
    .eq("task_name",task_name)
    .execute())
    return {"Updated the Task Details":response.data}

@app.delete("/tasks/{task_name}")
@limiter.limit(limit)
def delete_task(request: Request, task_name: str, current_user = Depends(get_current_user)):
    response = (
    supabase.table("tasks")
    .delete()
    .eq("task_name",task_name)
    .execute())
    return {"Task deleted successfully": response.data} 


@app.post("/url-shortner")
@limiter.limit(limit)
def url_shortner(request: Request, url: str, current_user = Depends(get_current_user)):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    response = (
    supabase.table("url_shortner")
    .insert({"url": url,"short_url": short_url,})
    .execute())
    inserted_data = response.data[0]
    return {"short_url": inserted_data["short_url"]}