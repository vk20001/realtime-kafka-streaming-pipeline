# import json
# import time
# import random
# import os
# from datetime import datetime
# from kafka import KafkaProducer
# from kafka.errors import NoBrokersAvailable

# KAFKA_BROKER = os.getenv(
#     "KAFKA_BROKER", "kafka:9092"
# )  # Make sure this is 'kafka' not 'localhost' in Docker
# KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "turbine-data")

# # --- Retry connection to Kafka ---
# producer = None
# for _ in range(10):
#     try:
#         producer = KafkaProducer(
#             bootstrap_servers=KAFKA_BROKER,
#             value_serializer=lambda v: json.dumps(v).encode("utf-8"),
#         )
#         print("✅ Kafka Producer connected.")
#         break
#     except NoBrokersAvailable:
#         print("⏳ Kafka broker not available. Retrying in 5 seconds...")
#         time.sleep(5)
# else:
#     raise Exception("❌ Could not connect to Kafka broker after multiple attempts.")


# def generate_turbine_data():
#     turbine_id = f"T-{random.randint(1, 15):03}"
#     wind_speed = round(random.uniform(3, 25), 2)
#     pitch_angle = round(random.uniform(0, 15), 2)
#     power_output = round((wind_speed**3) * 0.5 * random.uniform(0.85, 1.0), 2)
#     temperature = round(random.uniform(30, 90), 2)
#     vibration = round(random.uniform(0, 1), 2)

#     return {
#         "turbine_id": turbine_id,
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#         "wind_speed": wind_speed,
#         "pitch_angle": pitch_angle,
#         "power_output": power_output,
#         "temperature": temperature,
#         "vibration": vibration,
#     }


# if __name__ == "__main__":
#     print(f"🚀 Kafka Producer started. Sending data to topic: {KAFKA_TOPIC}")
#     while True:
#         data = generate_turbine_data()
#         print(f"[PRODUCER] Sent: {data}")
#         producer.send(KAFKA_TOPIC, value=data)
#         time.sleep(2)

"""
Wind-turbine sample‐data generator.

Key change:  ❌  NO KAFKA CONNECTION AT IMPORT TIME.
Instead we create the producer lazily inside `get_producer()`
so unit-tests don’t blow up when Kafka isn’t running (e.g. CI).
"""

from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime
from typing import Optional

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "turbine-data")
_RETRIES = 10                # connection attempts
_RETRY_SLEEP = 5             # seconds between attempts

# --------------------------------------------------------------------------- #
#  Producer is created lazily so an `import` alone never touches Kafka.
# --------------------------------------------------------------------------- #
_producer: Optional[KafkaProducer] = None


def _create_kafka_producer() -> KafkaProducer:
    """Create a KafkaProducer with retry logic."""
    for attempt in range(1, _RETRIES + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("✅ Kafka Producer connected.")
            return producer
        except NoBrokersAvailable:
            print(f"⏳ Kafka not available (attempt {attempt}/{_RETRIES}). Retrying…")
            time.sleep(_RETRY_SLEEP)
    raise RuntimeError("❌ Could not connect to Kafka after multiple attempts.")


def get_producer() -> KafkaProducer:
    """Return a singleton KafkaProducer, creating it on first use."""
    global _producer
    if _producer is None:
        _producer = _create_kafka_producer()
    return _producer


# --------------------------------------------------------------------------- #
#  Pure-data function – safe to import anywhere (including CI tests).
# --------------------------------------------------------------------------- #
def generate_turbine_data() -> dict[str, object]:
    turbine_id = f"T-{random.randint(1, 15):03}"
    wind_speed = round(random.uniform(3, 25), 2)
    pitch_angle = round(random.uniform(0, 15), 2)
    power_output = round((wind_speed**3) * 0.5 * random.uniform(0.85, 1.0), 2)
    temperature = round(random.uniform(30, 90), 2)
    vibration = round(random.uniform(0, 1), 2)

    return {
        "turbine_id": turbine_id,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "wind_speed": wind_speed,
        "pitch_angle": pitch_angle,
        "power_output": power_output,
        "temperature": temperature,
        "vibration": vibration,
    }


# --------------------------------------------------------------------------- #
#  CLI entry-point – only executed when you run the file directly.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    prod = get_producer()
    print(f"🚀 Producer loop started → topic: {KAFKA_TOPIC}")
    while True:
        msg = generate_turbine_data()
        print("[PRODUCER] Sent:", msg)
        prod.send(KAFKA_TOPIC, value=msg)
        time.sleep(2)
