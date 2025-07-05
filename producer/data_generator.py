import json
import time
import random
import os
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Make sure this is 'kafka' not 'localhost' in Docker
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "turbine-data")

# --- Retry connection to Kafka ---
producer = None
for _ in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("✅ Kafka Producer connected.")
        break
    except NoBrokersAvailable:
        print("⏳ Kafka broker not available. Retrying in 5 seconds...")
        time.sleep(5)
else:
    raise Exception("❌ Could not connect to Kafka broker after multiple attempts.")

def generate_turbine_data():
    turbine_id = f"T-{random.randint(1, 15):03}"
    wind_speed = round(random.uniform(3, 25), 2)
    pitch_angle = round(random.uniform(0, 15), 2)
    power_output = round((wind_speed ** 3) * 0.5 * random.uniform(0.85, 1.0), 2)
    temperature = round(random.uniform(30, 90), 2)
    vibration = round(random.uniform(0, 1), 2)

    return {
        "turbine_id": turbine_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "wind_speed": wind_speed,
        "pitch_angle": pitch_angle,
        "power_output": power_output,
        "temperature": temperature,
        "vibration": vibration
    }

if __name__ == "__main__":
    print(f"🚀 Kafka Producer started. Sending data to topic: {KAFKA_TOPIC}")
    while True:
        data = generate_turbine_data()
        print(f"[PRODUCER] Sent: {data}")
        producer.send(KAFKA_TOPIC, value=data)
        time.sleep(2)
