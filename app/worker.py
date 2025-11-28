import random
import time
from celery import Celery
from metrics import TASK_DURATION, TASK_COUNT
from config import get_redis_url, get_redis_ssl_config

# Initialize Celery with configurable Redis settings
celery_app = Celery(
    'tasks',
    broker=get_redis_url(),
    backend=get_redis_url(),
    broker_use_ssl=get_redis_ssl_config(),
    redis_backend_use_ssl=get_redis_ssl_config()
)

@celery_app.task(name='tasks.process_job')
def process_job():
    """
    Simulate a long-running job that takes 5-10 minutes to complete.
    """
    start_time = time.time()
    try:
        # Generate a random duration between 5-10 minutes
        duration = random.uniform(5 * 60, 10 * 60)
        
        # Simulate work by sleeping
        time.sleep(duration)
        
        # Generate some result data
        result = {
            "status": "completed",
            "duration": duration,
            "result_id": random.randint(1000, 9999),
            "completion_time": time.time()
        }
        
        # Record metrics
        TASK_DURATION.labels(task_name='process_job').observe(time.time() - start_time)
        TASK_COUNT.labels(task_name='process_job', status='success').inc()
        
        return result
    except Exception as e:
        # Record failure metrics
        TASK_DURATION.labels(task_name='process_job').observe(time.time() - start_time)
        TASK_COUNT.labels(task_name='process_job', status='failure').inc()
        raise e 