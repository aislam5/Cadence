from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from auth import getCredentials

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
        print("No upcoming events")
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

creds = getCredentials()
today = datetime.now(tz=timezone.utc)
start_date = today.replace(hour=8, minute=0, second=0, microsecond=0)
end_date = today + timedelta(days=7)
end_date = end_date.replace(hour=22, minute=0, second=0, microsecond=0)

events = getEvents(start_date, end_date, creds)
print(f"Found {len(events)} events")

free_blocks = get_free_busy_blocks(events, start_date, end_date)
for block in free_blocks:
    print(block)

    