import os
from urllib.parse import urlparse, parse_qs

def get_redis_url():
    """Get Redis URL from environment variable or use default"""
    default_url = "redis://redis:6379/0"
    redis_url = os.getenv('REDIS_URL', default_url)
    
    # Ensure the URL has the correct format
    if not redis_url.startswith(('redis://', 'rediss://')):
        redis_url = f"redis://{redis_url}"
    
    return redis_url

def get_redis_ssl_config():
    """Get Redis SSL configuration based on the URL scheme"""
    redis_url = get_redis_url()
    use_tls = redis_url.startswith('rediss://')
    
    if not use_tls:
        return None
    
    # Parse the URL to check for existing SSL parameters
    parsed_url = urlparse(redis_url)
    query_params = parse_qs(parsed_url.query)
    
    # If ssl_cert_reqs is already in the URL parameters, return None to avoid overriding
    if 'ssl_cert_reqs' in query_params:
        return None
        
    return {
        'ssl_cert_reqs': None,  # Don't require certificate verification for ElastiCache
    }

def get_server_port():
    """Get the server port from environment variables"""
    return int(os.getenv('SERVER_PORT', '8000')) 