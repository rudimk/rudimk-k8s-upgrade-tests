FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install K6

#RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 \
#    && echo "deb https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list \
#    && apt-get update \
#    && apt-get install -y k6 \
#    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt flower

# Copy application code, config, and load test script
COPY app/ .
COPY gunicorn.conf.py .
COPY flower.conf.py .
COPY k6/ /app/k6/

# Expose ports
EXPOSE 8000
EXPOSE 3000
EXPOSE 5555

# Command to run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]