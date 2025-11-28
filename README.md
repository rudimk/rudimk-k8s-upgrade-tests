# FastAPI with Celery Sample Application

This is a sample application that demonstrates a FastAPI web service with a Celery worker for background tasks.

## Features

- FastAPI web service with three endpoints:
  - `/healthz`: Health check endpoint
  - `/data`: Returns random data with a simulated delay
  - `/job`: Triggers a long-running Celery task
- Celery worker for processing background jobs
- Redis as message broker and result backend
- Docker setup for easy deployment
- Prometheus metrics endpoint at `/metrics`
- K6 load testing script
- Flower UI for Celery monitoring

## Prerequisites

- Python 3.8+
- Redis server (for message broker and result backend)
- Docker (optional, for containerized deployment)
- K6 (for load testing)

## Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL (e.g., `redis://host:port/db` or `rediss://host:port/db` for TLS) | `redis://redis:6379/0` |
| `SERVER_PORT` | Port number for the FastAPI server | `8000` |
| `WORKERS` | Number of gunicorn worker processes | CPU cores * 2 + 1 |
| `FLOWER_PORT` | Port number for the Flower UI | `5555` |

Example configuration for AWS ElastiCache:
```bash
export REDIS_URL=rediss://your-elasticache-endpoint.xxxxxx.ng.0001.use1.cache.amazonaws.com:6379/0
export SERVER_PORT=8080
export WORKERS=8
export FLOWER_PORT=5555
```

## Running the Application

### Option 1: Using Docker

1. Clone this repository
2. Build and run the Docker container:
   ```bash
   docker build -t fastapi-celery .
   docker run -p 8000:8000 -p 5555:5555 fastapi-celery
   ```

   Or with custom environment variables:
   ```bash
   docker run -p 8080:8080 -p 5555:5555 \
     -e SERVER_PORT=8080 \
     -e REDIS_URL=rediss://your-redis-host:6379/0 \
     -e WORKERS=8 \
     -e FLOWER_PORT=5555 \
     fastapi-celery
   ```

### Option 2: Running Locally

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server with gunicorn (in one terminal):
   ```bash
   gunicorn -c gunicorn.conf.py main:app
   ```

   Or with uvicorn directly (for development):
   ```bash
   cd app
   python main.py
   ```

5. Start the Celery worker (in another terminal):
   ```bash
   cd app
   celery -A worker worker --loglevel=info
   ```

6. Start the Flower UI (in another terminal):
   ```bash
   celery -A worker flower
   ```

   Note: Make sure Redis is running and accessible before starting the application.

## Monitoring with Flower

Flower is a web-based tool for monitoring Celery. It provides:

- Real-time monitoring of Celery workers and tasks through Redis
- Task history and statistics directly from the message broker
- Worker status and resource usage
- Task rate and execution time metrics
- Ability to revoke tasks
- Authentication and basic security features

To access the Flower UI:
1. Open your browser and navigate to `http://localhost:5555` (or your server's IP if running remotely)
2. You'll see a dashboard showing:
   - Active workers
   - Task queue status
   - Real-time task execution history from Redis
   - Worker resource usage
   - Live task updates

## Load Testing with K6

The repository includes a K6 load test script that alternates between calling the `/data` and `/job` endpoints. You can run the load test either locally or from within the container.

### Running Locally

1. Install K6:
   ```bash
   # macOS
   brew install k6
   
   # Linux
   sudo apt-get update && sudo apt-get install k6
   
   # Windows
   choco install k6
   ```

2. Run the load test:
   ```bash
   k6 run k6/load-test.js
   ```

   Or with a custom base URL:
   ```bash
   k6 run -e BASE_URL=http://your-server:8000 k6/load-test.js
   ```

### Running from Docker Container

The Docker image includes K6 and the load test script. You can run the load test from within the container:

```bash
# Build the image
docker build -t fastapi-celery .

# Run the load test against a running instance
docker run --rm -it \
  -e BASE_URL=http://your-server:8000 \
  fastapi-celery \
  k6 run /app/k6/load-test.js
```

Or run both the application and load test in separate containers:

```bash
# Start the application
docker run -d --name fastapi-app -p 8000:8000 -p 5555:5555 fastapi-celery

# Run the load test against it
docker run --rm -it \
  --network host \
  -e BASE_URL=http://localhost:8000 \
  fastapi-celery \
  k6 run /app/k6/load-test.js

# Clean up
docker stop fastapi-app
docker rm fastapi-app
```

The load test will:
- Start with 200 users
- Ramp up to 1000 users over 30 seconds
- Stay at 1000 users for 3 minutes
- Ramp up to 2000 users over 30 seconds
- Stay at 2000 users for 1 minute
- Ramp down to 100 users over 30 seconds
- Check that 95% of requests complete within 2 seconds
- Check that less than 1% of requests fail
- Add random delays between requests to simulate user think time

## API Endpoints

### Health Check
```
GET /healthz
```
Returns 200 if the service is healthy, 500 if it's shutting down.

### Random Data
```
GET /data
```
Returns random JSON data with a simulated delay of 1-3 seconds.

### Job Trigger
```
GET /job
```
Triggers a long-running Celery task that takes 5-10 minutes to complete.

### Metrics
```
GET /metrics
```
Exposes Prometheus metrics for Celery tasks and queue status.

## Architecture

- `app/main.py`: FastAPI application with all endpoints
- `app/worker.py`: Celery worker configuration and tasks
- `app/metrics.py`: Prometheus metrics collection
- `app/config.py`: Environment-based configuration
- `gunicorn.conf.py`: Gunicorn server configuration
- `flower.conf.py`: Flower monitoring configuration
- `Dockerfile`: Container configuration for the application
- `requirements.txt`: Python dependencies
- `k6/load-test.js`: K6 load testing script

## Development

To make changes to the application:

1. Modify the source files in the `app` directory
2. Rebuild and restart the container (if using Docker):
   ```bash
   docker build -t fastapi-celery .
   docker run -p 8000:8000 -p 5555:5555 fastapi-celery
   ```
   
   Or restart the local services:
   ```bash
   # Terminal 1 (FastAPI server)
   gunicorn -c gunicorn.conf.py app.main:app
   
   # Terminal 2 (Celery worker)
   cd app
   celery -A worker worker --loglevel=info
   
   # Terminal 3 (Flower UI)
   flower -A worker --conf=flower.conf.py
   ``` 