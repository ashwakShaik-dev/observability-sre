from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

@app.before_request
def before_request():
    from flask import g
    g.start_time = time.time()

@app.after_request
def after_request(response):
    from flask import request, g

    latency = time.time() - g.start_time

    logger.info(
        "Request: %s %s | Status: %s | Latency: %.3fs",
        request.method,
        request.path,
        response.status_code,
        latency
    )

    REQUEST_COUNT.labels(
        request.method,
        request.path,
        response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        request.method,
        request.path
    ).observe(latency)

    return response

@app.route("/")
def home():
    return "SRE Lab Application is running!"

health_broken = False

@app.route("/break")
def break_health():
    global health_broken
    health_broken = True
    return "Health check failure enabled", 500

@app.route("/fix")
def fix_health():
    global health_broken
    health_broken = False
    return "Health check restored", 200

@app.route("/health")
def health():
    if health_broken:
        return "unhealthy", 500
    return "healthy", 200

@app.route("/api")
def api():
    time.sleep(1)
    return "API response"

@app.route("/error")
def error():
    return "Internal Server Error", 500

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)