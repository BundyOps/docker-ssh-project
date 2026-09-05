# gunicorn.conf.py for Docker container
import multiprocessing
import os

# Server socket - bind to all interfaces in container
bind = "0.0.0.0:8000"

# Worker processes (2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Logging - use container-friendly paths
accesslog = "/app/logs/gunicorn-access.log"
errorlog = "/app/logs/gunicorn-error.log"
loglevel = "info"

# Process name
proc_name = "flask-weather-quote-app"

# Timeouts
timeout = 120
graceful_timeout = 30

# Maximum requests per worker
max_requests = 1000
max_requests_jitter = 100

# User/group (run as root in container for simplicity)
# user = "neptune"
# group = "www-data"

# Enable logging
capture_output = True
enable_stdio_inheritance = True
