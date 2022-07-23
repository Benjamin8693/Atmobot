import datetime
from zoneinfo import ZoneInfo

def get_formatted_time(timezone = "America/Panama"):
    return datetime.datetime.now(tz=ZoneInfo(timezone)).strftime("%H:%M:%S")
