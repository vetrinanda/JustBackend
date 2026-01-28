import os
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi import Request
from app.databse import supabase
from app.models import TaskCreate
# from sqlalchemy.orm import Session
import pyshorteners
from app.limiter import limiter

app = FastAPI()

# Create the database tables
# TTask.metadata.create_all(bind=engine)
# Url.metadata.create_all(bind=engine)

limit=os.getenv("LIMIT")


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
        
# db: Session = Depends(get_db)


app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management API"}


@app.get("/tasks/")
@limiter.limit(limit)
def read_tasks(request: Request):
    response = (
    supabase.table("tasks")
    .select("*")
    .execute()
)
    return response.data

@app.post("/tasks/")
@limiter.limit(limit)
def create_task(request: Request, task: TaskCreate):
    response = (
    supabase.table("tasks")
    .insert({"task_name": task.task_name,
             "task_description": task.task_description,
             "done_status": task.done_status})
    .execute())
    return {"Task Added Sucessfully": response.data}

@app.get("/tasks/done_status")
@limiter.limit(limit)
def get_task_status(request: Request,task_status: bool):
    response = (
    supabase.table("tasks")
    .select("*")
    .eq("done_status",task_status)
    .execute())
    return {"Response": response.data}


@app.get("/tasks/{task_name}")
@limiter.limit(limit)
def read_task(request: Request,task_name: str):
    response=(supabase.table("tasks")
              .select("*")
              .eq("task_name",task_name)
              .execute())
    return {"Reponse":response.data}

@app.put("/tasks/{task_name}")
@limiter.limit(limit)
def update_task(request: Request,task_name: str, task: TaskCreate):
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
def delete_task(request: Request,task_name: str):
    response = (
    supabase.table("tasks")
    .delete()
    .eq("task_name",task_name)
    .execute())
    return {"Task deleted successfully": response.data} 


@app.post("/url-shortner")
@limiter.limit(limit)
def url_shortner(request: Request,url:str):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    response = (
    supabase.table("url_shortner")
    .insert({"url": url,"short_url": short_url,})
    .execute())
    inserted_data = response.data[0]
    return {"short_url": inserted_data["short_url"]}