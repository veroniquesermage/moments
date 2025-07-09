from datetime import datetime
from zoneinfo import ZoneInfo


def is_expired(date: datetime) -> bool:
    return date < now_paris()

def now_paris():
    return datetime.now(ZoneInfo("Europe/Paris"))
