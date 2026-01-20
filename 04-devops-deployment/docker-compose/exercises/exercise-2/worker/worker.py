"""Worker for health check exercise."""

import os
import time

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://localhost:5672")

print(f"Worker starting, connecting to {RABBITMQ_URL}")

# Simulate worker running
while True:
    print("Worker processing...")
    time.sleep(10)
