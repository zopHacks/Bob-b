from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_datetime_in_timezone(timezone_str):
    """
    Returns the current date and time in a specified timezone.
    Format: YYYY-MM-DDTHH:MM:SS±HH:MM
    """
    try:
        now = datetime.now(ZoneInfo(timezone_str))
        return now.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO 8601 format with timezone offset
    except ValueError:
        return "Invalid timezone!"

timezone = "Asia/Jerusalem"
current_time = get_current_datetime_in_timezone(timezone)
print("Current Date and Time:", current_time)

