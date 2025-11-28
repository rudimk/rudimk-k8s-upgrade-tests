import os
import multiprocessing

# Get the port from environment variable or default to 8000
bind = f"0.0.0.0:{os.getenv('SERVER_PORT', '8000')}"

# Get the number of workers from environment variable or calculate based on CPU cores
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Use uvicorn workers for ASGI support
worker_class = "uvicorn.workers.UvicornWorker"

# Logging configuration
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Timeout settings
timeout = 120
keepalive = 5 