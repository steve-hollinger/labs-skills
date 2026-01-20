"""Simple Flask application for Dockerfile optimization exercise."""

from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "Hello from Flask!", "user": os.getenv("USER", "unknown")})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
