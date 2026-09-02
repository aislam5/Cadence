from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from auth import getCredentials
from zoneinfo import ZoneInfo

def getEvents(startDate, endDate, creds):
    service = build("calendar", "v3", credentials=creds)
    events = service.events().list(
        calendarId = "primary",
        timeMin = startDate.isoformat(),
        timeMax=endDate.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    eventsList = events.get("items", [])

    if not eventsList:
        return []
    return eventsList

def get_free_busy_blocks(events, start_date, end_date):
    gaps = []
    endPrevious = start_date
    for event in events:
        start = datetime.fromisoformat(event["start"].get("dateTime", event["start"]))
        end = datetime.fromisoformat(event["end"].get("dateTime", event["end"]))
        if  start > endPrevious:
            gap = {"start":endPrevious, "end":start}
            gaps.append(gap)
        endPrevious = end
    if end_date > endPrevious:
        gaps.append({"start": endPrevious, "end": end_date})
    return gaps


def get_week_free_blocks(start_date, end_date, creds):
    week_free_blocks = []
    how_many_days = (end_date - start_date).days
    for i in range(0, how_many_days+1):
        next_days = start_date + timedelta(days=i)
        new_start_day = next_days.replace(hour=8, minute=0, second=0, microsecond=0)
        new__end_date = next_days.replace(hour=22, minute=0, second=0, microsecond=0)
        events = getEvents(new_start_day, new__end_date, creds)
        free_blocks = get_free_busy_blocks(events, new_start_day, new__end_date)
        week_free_blocks.extend(free_blocks)
    return week_free_blocks

if __name__ == "__main__":
    creds = getCredentials()
    today = datetime.now(tz=ZoneInfo("America/New_York"))
    start_date = today.replace(hour=8, minute=0, second=0, microsecond=0)
    end_date = (today + timedelta(days=7)).replace(hour=22, minute=0, second=0, microsecond=0)

    blocks = get_week_free_blocks(start_date, end_date, creds)
    for block in blocks:
        print(block)