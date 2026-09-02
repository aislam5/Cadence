from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import getCredentials
from calendarClient import getEvents, get_free_busy_blocks, get_week_free_blocks
from datetime import datetime, timezone, timedelta
from schemas import IntakeRequest
from agents.intake_agent import parse_goals
from zoneinfo import ZoneInfo
from agents.scheduler_agent import propose_schedule

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # match your actual Vite port
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
  )

@app.get("/health")
async def root():
    return{"status":"ok"}

@app.get("/calendar/week")
def get_week():
    creds = getCredentials()
    today = datetime.now(tz=ZoneInfo("America/New_York"))
    start_date = today.replace(hour=8, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=7)
    end_date = end_date.replace(hour=22, minute=0, second=0, microsecond=0)
  
    events = getEvents(start_date, end_date, creds)
    free_blocks = get_free_busy_blocks(events, start_date, end_date)

    return{
      "events": events,  
      "free_blocks" :free_blocks
    }

@app.post("/agents/intake")
def handle_post(request: IntakeRequest):
    goals = request.raw_text
    taskList = parse_goals(goals)
    return taskList

@app.post("/agents/schedule")
def handle_post(request: IntakeRequest):
    goals = request.raw_text
    tasks = parse_goals(goals)
    today = datetime.now(tz=ZoneInfo("America/New_York"))
    start_date = today.replace(hour=8, minute=0, second=0, microsecond=0)
    end_date = (today + timedelta(days=7)).replace(hour=22, minute=0, second=0, microsecond=0)
    creds = getCredentials()
    freeBlocks = get_week_free_blocks(start_date, end_date, creds)
    proposedSchedule = propose_schedule(tasks, freeBlocks)
    return proposedSchedule
