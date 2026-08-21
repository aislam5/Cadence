from  schemas import TaskList
from google import genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


PROMPT_TEMPLATE = f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.""""You are a task extraction assistant. Convert the user's free-text description of their goals and responsibilities into a structured JSON list of tasks.

Each task must have exactly these fields:
- title (string): short name for the task
- duration_minutes (integer): realistic estimated time to complete it
- priority (integer, 1-5): 5 is most urgent/important, 1 is least
- category (string): one of "work", "health", "personal", "social", "learning"
- deadline (string or null): ISO date if a deadline is mentioned or implied, otherwise null

Respond with ONLY valid JSON in this exact shape, no markdown formatting, no explanation:
{{"tasks": [{{"title": "...", "duration_minutes": ..., "priority": ..., "category": "...", "deadline": ...}}]}}

Example:
Input: "I need to study for my algorithms exam next Friday, probably need like 3 sessions, and I should really start going to the gym again."
Output: {{"tasks": [{{"title": "Study for algorithms exam", "duration_minutes": 90, "priority": 5, "category": "learning", "deadline": "2026-08-28"}}, {{"title": "Gym session", "duration_minutes": 60, "priority": 3, "category": "health", "deadline": null}}]}}

Now convert this input:
{raw_text}
"""

def parse_goals(raw_text: str) -> TaskList:
    prompt = PROMPT_TEMPLATE.format(raw_text=raw_text)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    raw_output = response.text.strip()

    try:
        return TaskList.model_validate_json(raw_output)
    except Exception as first_error:
        retry_prompt = prompt + f"\n\nYour previous response failed to parse as a valid JSON with this error: {first_error}. Respond again with ONLY valid JSON, not markdown fences, no explanation."
        retry_response = client.models.generate_content(
            model="gemini--3.6-flash",
            contents=retry_prompt
        )
        return TaskList.model_validate_json(retry_response.text.strip())

