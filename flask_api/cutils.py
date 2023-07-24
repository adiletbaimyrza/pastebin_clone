# cutils = custom utilities
from datetime import datetime, timedelta


def add_utc_minutes(utc_time: datetime, minutes_to_add: int) -> datetime:
    # create a timedelta object representing duration in time
    time_delta = timedelta(minutes=minutes_to_add)

    # add timedelta duration to utc_time
    new_utc_time = utc_time + time_delta

    return new_utc_time


def is_expired(expiration_time: datetime) -> bool:
    # compare expiration_time to now
    return True if expiration_time < datetime.utcnow() else False
