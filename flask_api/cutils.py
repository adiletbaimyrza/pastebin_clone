# cutils = custom utilities
import os
from datetime import datetime, timedelta
import base64
from base64 import urlsafe_b64encode, urlsafe_b64decode, encode, decode


def add_utc_minutes(utc_time: datetime, minutes_to_add: int) -> datetime:
    # create a timedelta object representing duration in time
    time_delta = timedelta(minutes=minutes_to_add)

    # add timedelta duration to utc_time
    new_utc_time = utc_time + time_delta

    return new_utc_time


def is_expired(expiration_time: datetime) -> bool:
    # compare expiration_time to now
    return True if expiration_time < datetime.utcnow() else False


def to_bytes_like_object(string_object: str):
    return string_object.encode()


def generate_short_url_hash(id: str, length=8):
    # bytes-like object
    blo_object = to_bytes_like_object(id)
    hash = base64.urlsafe_b64encode(blo_object)
    short_hash = hash[-length:].decode()

    return short_hash


def create_paste(file_name: str, text: str):
    # Get the current directory where the main.py file is located
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create a new directory named "txt_files" if it doesn't exist
    pastes_directory = os.path.join(current_directory, "pastes")

    # Create the full path for the new .txt file inside the "txt_files" directory
    file_path = os.path.join(pastes_directory, file_name)

    # Write some content to the file (optional)
    with open(file_path, 'w') as file:
        file.write(text)

    return file_path


def read_txt(file_path):
    with open(file_path, 'r') as file:
        # Read the entire content of the file using read()
        file_content = file.read()
        return file_content


def get_from_cache(redis_client, key):
    data = redis_client.get(key)
    if data:
        print(f"From Cache: {key}")
    return data


def set_to_cache(redis_client, key, value, expiration=20):
    redis_client.setex(key, expiration, value)
    print(f"Set to Cache: {key}")
