from schemas import TaskList
from agents.intake_agent import parse_goals
from calendarClient import get_week_free_blocks
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from auth import getCredentials
from typing import TypedDict
from agents.scheduler_agent import propose_schedule
from langgraph.graph import StateGraph, START, END


class PlannerState(TypedDict):
    raw_goals : str
    tasks : TaskList | None
    free_blocks : list | None
    schedule : list | None

def intake_node(state: PlannerState) -> dict:
    tasks = parse_goals(state["raw_goals"])
    return {"tasks" : tasks}

def calendar_node(state : PlannerState) -> dict:
    creds = getCredentials()
    today = datetime.now(tz=ZoneInfo("America/New_York"))
    start_date = today.replace(hour=8, minute=0, second=0, microsecond=0)
    end_date = (today + timedelta(days=7)).replace(hour=22, minute=0, second=0, microsecond=0)
    free_blocks = get_week_free_blocks(start_date, end_date, creds)
    return {"free_blocks" : free_blocks}

def scheduler_node(state : PlannerState):
    schedule = propose_schedule(state["tasks"], state["free_blocks"])
    return {"schedule" : schedule}

def build_graph():
    graph_builder = StateGraph(PlannerState)

    graph_builder.add_node("intake", intake_node)
    graph_builder.add_node("calendar", calendar_node)
    graph_builder.add_node("scheduler", scheduler_node)

    graph_builder.add_edge(START, "intake")
    graph_builder.add_edge("intake", "calendar")
    graph_builder.add_edge("calendar", "scheduler")
    graph_builder.add_edge("scheduler", END)

    graph = graph_builder.compile()
    return graph

if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({"raw_goals": "This week I need to finish my portfolio project's README, and I have a group meeting for my software engineering class on Tuesday I need to prepare slides for. I also want to go for a run at least twice, and I've got a dentist appointment Thursday afternoon that I really can't miss. Somewhere in there I should also review pull requests for my open source contribution before the weekend."})
    print("Tasks:", result["tasks"])
    print("Free blocks:", result["free_blocks"])
    print("Schedule:", result["schedule"])

#This week I need to finish my portfolio project's README, and I have a group meeting for my software engineering class on Tuesday I need to prepare slides for. I also want to go for a run at least twice, and I've got a dentist appointment Thursday afternoon that I really can't miss. Somewhere in there I should also review pull requests for my open source contribution before the weekend.

