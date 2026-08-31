from pydantic import BaseModel, Field
import uuid

class Task(BaseModel):
    id : str = Field(default_factory=lambda: str(uuid.uuid4()))
    title : str
    duration_minutes: int
    priority: int 
    category : str
    deadline : str | None

class TaskList(BaseModel):
    tasks: list[Task]

class IntakeRequest(BaseModel):
    raw_text:str

class ScheduledTask(BaseModel):
    task_id: str
    start: str
    end: str

class ScheduleResult(BaseModel):
    scheduled: list[ScheduledTask]
    unscheduled: list[str]