# cutils = custom utilities
import os
from datetime import datetime, timedelta
import base64
from base64 import urlsafe_b64encode, urlsafe_b64decode, encode, decode


def add_utc_time(utc_time: datetime, time_unit: str, time_value: int):
    if time_unit is None:
        return None
    if time_value is None:
        return None
    
    time_units_to_timedeltas = {
        'minutes': timedelta(minutes=time_value),
        'hours': timedelta(hours=time_value),
        'days': timedelta(days=time_value)
    }
    
    time_delta = time_units_to_timedeltas.get(time_unit)

    new_utc_time = utc_time + time_delta

    return new_utc_time



def is_expired(expiration_time) -> bool:
    # compare expiration_time to now
    if expiration_time is None:
        return False
    return True if expiration_time < datetime.utcnow() else False


def to_bytes_like_object(string_object: str):
    return string_object.encode()


def generate_short_url_hash(id: str, length=8) -> str:
    # bytes-like object
    blo_object = to_bytes_like_object(id)
    hash = base64.urlsafe_b64encode(blo_object)
    short_hash = hash[-length:].decode()

    return short_hash
