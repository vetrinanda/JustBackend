from sqlalchemy import Column, Integer, String, Text,Boolean
from app.databse import Base

class TTask(Base):
    __tablename__ = "tasks"
    id: int = Column(Integer, primary_key=True, index=True)
    task_name: str = Column(String, index=True)
    task_description: str = Column(Text)
    done_status: bool = Column(Boolean, index=True)
    
    
class Url(Base):
    __tablename__="url"
    id:int =Column(Integer,primary_key=True,index=True)
    url:str=Column(String,index=True)
    shorturl:str=Column(String,index=True)