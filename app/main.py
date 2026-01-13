from fastapi import FastAPI, Depends, HTTPException,status
from app.databse import supabase
from app.models import TaskCreate
# from sqlalchemy.orm import Session
import pyshorteners

app = FastAPI()

# Create the database tables
# TTask.metadata.create_all(bind=engine)
# Url.metadata.create_all(bind=engine)




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
def read_tasks():
    response = (
    supabase.table("tasks")
    .select("*")
    .execute()
)
    return response.data

@app.post("/tasks/")
def create_task(task: TaskCreate):
    response = (
    supabase.table("tasks")
    .insert({"task_name": task.task_name,
             "task_description": task.task_description,
             "done_status": task.done_status})
    .execute())
    return {"Task Added Sucessfully": response.data}

@app.get("/tasks/done_status")
def get_task_status(task_status: bool):
    response = (
    supabase.table("tasks")
    .select("*")
    .eq("done_status",task_status)
    .execute())
    return {"Response": response.data}


@app.get("/tasks/{task_name}")
def read_task(task_name: str):
    response=(supabase.table("tasks")
              .select("*")
              .eq("task_name",task_name)
              .execute())
    return {"Reponse":response.data}

@app.put("/tasks/{task_name}")
def update_task(task_name: str, task: TaskCreate):
    response = (
    supabase.table("tasks")
    .update({"task_name": task.task_name,
             "task_description": task.task_description,
             "done_status": task.done_status})
    .eq("task_name",task_name)
    .execute())
    return {"Updated the Task Details":response.data}

@app.delete("/tasks/{task_name}")
def delete_task(task_name: str):
    response = (
    supabase.table("tasks")
    .delete()
    .eq("task_name",task_name)
    .execute())
    return {"Task deleted successfully": response.data} 


@app.post("/url-shortner")
def url_shortner(url:str):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(url)
    response = (
    supabase.table("url_shortner")
    .insert({"url": url,"short_url": short_url,})
    .execute())
    inserted_data = response.data[0]
    return {"short_url": inserted_data["short_url"]}