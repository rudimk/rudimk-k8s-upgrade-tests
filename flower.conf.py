import os

# Flower configuration
broker_api = os.getenv('REDIS_URL', 'redis://redis:6379/0')  # Use the same Redis URL as the application
address = '0.0.0.0'
port = 5555
url_prefix = ''
max_tasks = 10000
persistent = False  # Disable persistence since we're using Redis
basic_auth = None  # Disable authentication by default 