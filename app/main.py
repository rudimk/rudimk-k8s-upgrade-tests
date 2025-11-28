import random
import time
import json
import signal
import asyncio
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from celery import Celery
import os
from metrics import get_metrics
from config import get_redis_url, get_redis_ssl_config, get_server_port

# Global variable to track app readiness
app_ready = True
shutdown_event = asyncio.Event()

# Signal handler for graceful shutdown
def handle_shutdown(signum, frame):
    global app_ready
    app_ready = False
    shutdown_event.set()
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")

# Register signal handlers before creating the FastAPI app
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# Initialize FastAPI app
app = FastAPI()

# Initialize Celery with configurable Redis settings
celery_app = Celery(
    'tasks',
    broker=get_redis_url(),
    backend=get_redis_url(),
    broker_use_ssl=get_redis_ssl_config(),
    redis_backend_use_ssl=get_redis_ssl_config()
)

@app.on_event("shutdown")
async def shutdown_event_handler():
    """Clean up resources on shutdown"""
    logger = logging.getLogger(__name__)
    logger.info("Shutting down application...")
    # Add any cleanup code here if needed

@app.get("/healthz")
async def health_check():
    if not app_ready:
        raise HTTPException(status_code=500, detail="Service is shutting down")
    return {"status": "healthy"}

@app.get("/data")
async def get_random_data():
    # Check if we're shutting down
    if not app_ready:
        raise HTTPException(status_code=503, detail="Service is shutting down")
    
    # Simulate random delay between 1-3 seconds
    delay = random.uniform(1, 3)
    await asyncio.sleep(delay)
    
    # Generate random data
    data = {
        "id": random.randint(1, 1000),
        "name": f"Item_{random.randint(1, 100)}",
        "value": random.uniform(0, 100),
        "timestamp": time.time(),
        "metadata": {
            "category": random.choice(["A", "B", "C", "D"]),
            "tags": [f"tag_{i}" for i in range(random.randint(1, 5))]
        }
    }
    return data

@app.get("/job")
async def trigger_job():
    # Check if we're shutting down
    if not app_ready:
        raise HTTPException(status_code=503, detail="Service is shutting down")
    
    # Trigger the Celery task
    task = celery_app.send_task('tasks.process_job')
    return {"task_id": task.id, "status": "Job started"}

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Expose Prometheus metrics"""
    return get_metrics()

if __name__ == "__main__":
    port = get_server_port()
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=5,
        timeout_graceful_shutdown=30
    )
    server = uvicorn.Server(config)
    server.run() 