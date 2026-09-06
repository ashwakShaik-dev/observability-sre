from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

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


@app.route("/health")
def health():
    return "healthy"


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