from schemas import ScheduledTask, ScheduleResult, TaskList
from google import genai
import os 
from dotenv import load_dotenv
from datetime import datetime
from calendarClient import get_free_busy_blocks

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PROMPT_TEMPLATE = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.""""You are a scheduling assistant. Given a list of tasks and a list of available free time blocks, assign each task to a specific start and end time.

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    raw_output = response.text.strip()

    return