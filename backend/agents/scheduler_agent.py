from schemas import ScheduleResult, TaskList
from google import genai
import os 
from dotenv import load_dotenv
from datetime import datetime
from calendarClient import get_week_free_blocks
import json
from zoneinfo import ZoneInfo

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT_TEMPLATE = "Today's date is {today}" """You are a scheduling assistant. Given a list of tasks and a list of available free time blocks, assign each task to a specific start and end time.

Rules:
- Every task must fit entirely within a single free time block — never overlapping a busy period.
- No two scheduled tasks may overlap each other.
- Respect each task's duration_minutes exactly — do not shorten or lengthen it.
- Prioritize placing higher-priority tasks (priority 5) and tasks with near deadlines earlier in the week, before lower-priority tasks.
- If a task cannot fit anywhere in the available free blocks, omit it from the output and instead list it separately as "unscheduled".
- Use ISO 8601 datetime format for all start/end times.

Tasks:
{tasks_json}

Available free time blocks:
{free_blocks_json}

Respond with ONLY valid JSON in this exact shape, no markdown formatting, no explanation:
{{"scheduled": [{{"task_id": "...", "start": "...", "end": "..."}}], "unscheduled": ["task_id", ...]}}
"""



def propose_schedule(tasks: TaskList, free_blocks: list) -> ScheduleResult:
    prompt = PROMPT_TEMPLATE.format(
                today= datetime.now(tz=ZoneInfo("America/New_York")).strftime('%Y-%m-%d'),
                tasks_json= tasks.model_dump_json(), 
                free_blocks_json=json.dumps(free_blocks, default=str))
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    raw_output = response.text.strip()
    try:
        return ScheduleResult.model_validate_json(raw_output)
    except Exception as first_error:
        retry_prompt = prompt + f"\n\nYour previous response failed to parse as a valid JSON with this error: {first_error}. Respond again with ONLY valid JSON, not markdown fences, no explanation."
        retry_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=retry_prompt
        )
        return ScheduleResult.model_validate_json(retry_response.text.strip())

