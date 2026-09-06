from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "SRE Lab Application is running!"

@app.route("/health")
def health():
    return "healthy"

@app.route("/api")
def api():
    return "API response"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)