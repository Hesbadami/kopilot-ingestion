bind = ["127.0.0.1:8002"]
workers = 3
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "django-app"
group = "django-app"

# Logging
accesslog = "/var/log/kopilot/kopilot_ingestion/access.log"
errorlog = "/var/log/kopilot/kopilot_ingestion/error.log"
loglevel = "info"

# Process management
pidfile = "/var/run/kopilot/kopilot_ingestion.pid"
daemon = False  # Let systemd handle daemonization

# Graceful restarts
graceful_timeout = 30