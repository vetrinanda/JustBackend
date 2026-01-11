from fastapi import FastAPI, Depends, HTTPException,status
from app.databse import engine, Base, SessionLocal
from app.models import TTask
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()

# Create the database tables
TTask.metadata.create_all(bind=engine)

class TaskCreate(BaseModel):
    task_name: str
    task_description: str
    done_status: bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# db: Session = Depends(get_db)


app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management API"}


@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TTask).all()
    return tasks

@app.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = TTask(task_name=task.task_name, task_description=task.task_description, done_status=task.done_status)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/done_status")
def get_task_status(task_status: bool, db: Session = Depends(get_db)):
    tasks = db.query(TTask).filter(TTask.done_status == task_status).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found with this status")
    return tasks


@app.get("/tasks/{task_name}")
def read_task(task_name: str, db: Session = Depends(get_db)):
    task = db.query(TTask).filter(TTask.task_name == task_name).first()
    if task is None:
        return {"error": "Task not found"}
    return task

@app.put("/tasks/{task_name}")
def update_task(task_name: str, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(TTask).filter(TTask.task_name == task_name).first()
    if db_task is None:
        return {"error": "Task not found"}
    db_task.task_name = task.task_name
    db_task.task_description = task.task_description
    db_task.done_status = task.done_status
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_name}")
def delete_task(task_name: str, db: Session = Depends(get_db)):
    db_task = db.query(TTask).filter(TTask.task_name == task_name).first()
    if db_task is None:
        return {"error": "Task not found"}
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"} 


