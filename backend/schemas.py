from pydantic import BaseModel

class Task(BaseModel):
    title : str
    duration_minutes: int
    priority: int 
    category : str
    deadline : str | None

class TaskList(BaseModel):
    tasks: list[Task]

class IntakeRequest(BaseModel):
    raw_text:str