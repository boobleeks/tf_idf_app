import time
from .metrics import record_processing_time

def track_processing_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        response = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        record_processing_time(duration)
        return response
    return wrapper