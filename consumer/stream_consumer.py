import os
import json
import logging
import time
import threading
import pandas as pd
import pandera.errors as pa_errors
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from schema import turbine_schema
from sqlalchemy import create_engine, text
import sqlalchemy.exc
from dotenv import load_dotenv
from prometheus_client import start_http_server, Counter

# === Load .env ===
load_dotenv()

# === Logging Setup ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/consumer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# === Environment Variables ===
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# === SQLAlchemy Connection ===
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# === Prometheus Metrics ===
start_http_server(
    8000, addr="0.0.0.0"
)  # Exposes metrics on http://localhost:8000/metrics
messages_processed = Counter(
    "turbine_messages_valid", "Number of valid messages processed"
)
messages_invalid = Counter("turbine_messages_invalid", "Number of invalid messages")
db_inserts = Counter("turbine_db_inserts", "Successful DB inserts")


# === Heartbeat Thread ===
def heartbeat():
    while True:
        logging.info("⏱️ Heartbeat: consumer is alive and waiting for messages...")
        time.sleep(15)  # Feel free to adjust if needed


threading.Thread(target=heartbeat, daemon=True).start()

# === Create Table (if not exists) with Retry ===
TABLE_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS turbine_data (
    id SERIAL PRIMARY KEY,
    turbine_id VARCHAR(10),
    timestamp TIMESTAMP,
    wind_speed FLOAT,
    pitch_angle FLOAT,
    power_output FLOAT,
    temperature FLOAT,
    vibration FLOAT
);
"""

for _ in range(10):
    try:
        with engine.begin() as conn:
            conn.execute(text(TABLE_CREATE_SQL))
            logging.info("✅ Ensured turbine_data table exists in DB.")
            break
    except sqlalchemy.exc.OperationalError as e:
        logging.warning(f"Postgres not ready yet: {e}. Retrying in 5s...")
        time.sleep(5)
else:
    raise Exception("❌ Could not connect to PostgreSQL after multiple attempts.")

# === Kafka Consumer with Retry ===
consumer = None
for _ in range(10):
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="wind-consumer-group",
        )
        logging.info("✅ Kafka Consumer connected.")
        break
    except NoBrokersAvailable:
        print("⏳ Kafka broker not available. Retrying in 5 seconds...")
        time.sleep(5)
else:
    raise Exception("❌ Could not connect to Kafka broker after multiple attempts.")

# === Stream + Validate + Store + Metrics ===
for message in consumer:
    data = message.value
    try:
        df = pd.DataFrame([data])
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        validated = turbine_schema.validate(df)

        validated.to_sql("turbine_data", engine, if_exists="append", index=False)

        messages_processed.inc()
        db_inserts.inc()
        logging.info(
            f"[VALID ✅] Stored to DB: {validated.to_dict(orient='records')[0]}"
        )

    except pa_errors.SchemaError as e:
        messages_invalid.inc()
        logging.error(f"[INVALID ❌] {data}")
        logging.error(f"Schema error: {str(e)}")

    except Exception as e:
        logging.error(f"💥 DB Insert Error: {str(e)} | Data: {data}")
