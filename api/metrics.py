import time
import threading


lock = threading.Lock()
metrics_data = {
    'files_processed': 0,
    'times': [],  
    'latest_file_processed_timestamp': None
}

def record_processing_time(duration: float):
    with lock:
        metrics_data['files_processed'] += 1
        metrics_data['times'].append(duration)
        metrics_data['latest_file_processed_timestamp'] = int(time.time())

def get_metrics():
    with lock:
        times = metrics_data['times']
        if not times:
            return {
                'files_processed': 0,
                'min_time_processed': 0.0,
                'avg_time_processed': 0.0,
                'max_time_processed': 0.0,
                'latest_file_processed_timestamp': None,
            }
        return {
            'files_processed': metrics_data['files_processed'],
            'min_time_processed': round(min(times), 3),
            'avg_time_processed': round(sum(times) / len(times), 3),
            'max_time_processed': round(max(times), 3),
            'latest_file_processed_timestamp': metrics_data['latest_file_processed_timestamp'],
        }
