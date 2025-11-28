from prometheus_client import Counter, Histogram, Gauge, generate_latest
from celery import Celery
import time
import redis
import logging
from config import get_redis_url, get_redis_ssl_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery with configurable Redis settings
celery_app = Celery(
    'tasks',
    broker=get_redis_url(),
    backend=get_redis_url(),
    broker_use_ssl=get_redis_ssl_config(),
    redis_backend_use_ssl=get_redis_ssl_config()
)

# Initialize Redis client for queue inspection
redis_url = get_redis_url()
ssl_config = get_redis_ssl_config()
redis_client = redis.from_url(redis_url, **ssl_config if ssl_config else {})

# Define Prometheus metrics
TASK_DURATION = Histogram(
    'celery_task_duration_seconds',
    'Time spent processing Celery tasks',
    ['task_name']
)

TASK_COUNT = Counter(
    'celery_task_total',
    'Total number of Celery tasks processed',
    ['task_name', 'status']
)

TASK_QUEUE_LENGTH = Gauge(
    'celery_queue_length',
    'Number of tasks in the queue',
    ['queue_name']
)

TASK_ACTIVE = Gauge(
    'celery_active_tasks',
    'Number of active tasks',
    ['worker_name']
)

TASK_SCHEDULED = Gauge(
    'celery_scheduled_tasks',
    'Number of scheduled tasks',
    ['worker_name']
)

TASK_RESERVED = Gauge(
    'celery_reserved_tasks',
    'Number of reserved tasks',
    ['worker_name']
)

def get_metrics():
    """Collect and return Celery metrics"""
    try:
        # Reset all metrics to 0
        TASK_QUEUE_LENGTH.clear()
        TASK_ACTIVE.clear()
        TASK_SCHEDULED.clear()
        TASK_RESERVED.clear()
        
        # Get queue length from Redis using Celery's queue naming convention
        queue_name = 'celery'  # Default queue name
        try:
            # Get the actual queue length from Redis
            queue_length = redis_client.llen(f'celery:{queue_name}')
            logger.info(f"Queue length for {queue_name}: {queue_length}")
            TASK_QUEUE_LENGTH.labels(queue_name=queue_name).set(queue_length)
        except redis.RedisError as e:
            logger.error(f"Error getting queue length from Redis: {e}")
            TASK_QUEUE_LENGTH.labels(queue_name=queue_name).set(0)
        
        # Get active tasks
        try:
            active_tasks = celery_app.control.inspect().active()
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    logger.info(f"Active tasks on worker {worker}: {len(tasks)}")
                    TASK_ACTIVE.labels(worker_name=worker).set(len(tasks))
            else:
                logger.info("No active tasks found")
        except Exception as e:
            logger.error(f"Error getting active tasks: {e}")
        
        # Get scheduled tasks
        try:
            scheduled_tasks = celery_app.control.inspect().scheduled()
            if scheduled_tasks:
                for worker, tasks in scheduled_tasks.items():
                    logger.info(f"Scheduled tasks on worker {worker}: {len(tasks)}")
                    TASK_SCHEDULED.labels(worker_name=worker).set(len(tasks))
            else:
                logger.info("No scheduled tasks found")
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {e}")
        
        # Get reserved tasks
        try:
            reserved_tasks = celery_app.control.inspect().reserved()
            if reserved_tasks:
                for worker, tasks in reserved_tasks.items():
                    logger.info(f"Reserved tasks on worker {worker}: {len(tasks)}")
                    TASK_RESERVED.labels(worker_name=worker).set(len(tasks))
            else:
                logger.info("No reserved tasks found")
        except Exception as e:
            logger.error(f"Error getting reserved tasks: {e}")
        
        return generate_latest()
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        raise 