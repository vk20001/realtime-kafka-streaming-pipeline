# ⚡ Real-Time Kafka Streaming Pipeline

A production-grade, containerized real-time data pipeline for ingesting, validating, and storing wind turbine telemetry using Apache Kafka, Python, PostgreSQL, and Prometheus/Grafana. This project is fully CI/CD enabled and structured to reflect modern industry standards in data engineering.

## 🚀 Overview

This pipeline simulates a real-world wind turbine monitoring system:

- Simulated sensor data is produced and streamed via Kafka.
- A Kafka consumer receives, validates, and stores the data in PostgreSQL.
- Pandera enforces schema validation for data quality.
- Prometheus scrapes metrics exposed by the consumer.
- Grafana visualizes real-time health of the pipeline.
- GitHub Actions powers continuous integration with automated linting and testing.

## 🧱 Architecture

Producer → Kafka → Consumer → PostgreSQL  
                        ↳ Schema Validation (Pandera)  
                        ↳ Monitoring (Prometheus + Grafana)

## 🛠 Tech Stack

Messaging: Apache Kafka, Zookeeper  
Data Simulation: Python Kafka Producer  
Ingestion & Logic: Python Consumer, Pandera Schema Validation  
Storage: PostgreSQL  
Monitoring: Prometheus, Grafana  
Containerization: Docker, Docker Compose  
CI/CD: GitHub Actions, flake8, pytest  

## ✅ Features

- Real-time message streaming with Kafka
- Pandera-based schema enforcement
- PostgreSQL persistence for clean, validated records
- Prometheus metrics with Grafana dashboards
- Flake8 linting and Pytest unit tests
- GitHub Actions CI pipeline for robust automation
- Modular, production-grade folder structure

## 📦 Getting Started

### 1. Requirements

- Docker & Docker Compose
- Python 3.11+ (optional for local test execution)
- Free ports: 9092, 5432, 9090, 3000

### 2. Setup & Run

Clone the repo and launch the entire pipeline:

```bash
git clone https://github.com/vk20001/realtime-wind-streaming-pipeline.git
cd realtime-wind-streaming-pipeline
docker compose up --build
```

### 3. Access Points

Grafana: http://localhost:3000  
Prometheus: http://localhost:9090  
PostgreSQL: localhost:5432 (use DBeaver or psql)  
Kafka Broker: localhost:9092  

## 🔬 Testing & Linting

Run locally:  
```bash
pytest consumer/tests/
flake8 .
```

CI/CD via GitHub Actions ensures automated testing and formatting on every push.

## 📊 Observability Metrics

Prometheus metrics exposed by the consumer:  
- `messages_total`: All Kafka messages received  
- `messages_valid`: Messages that passed validation  
- `messages_invalid`: Messages that failed validation  

These are visualized in Grafana with live updates.

## 📁 Project Structure

```
consumer/              → Kafka consumer and schema logic
└── tests/             → Unit and integration tests
producer/              → Kafka producer for simulated turbine data
monitoring/            → Prometheus & Grafana configs
scripts/               → Utility scripts
.github/workflows/     → GitHub Actions CI workflow
docker-compose.yml     → Service orchestration
.flake8                → Linting configuration
.env                   → Environment variables
.gitignore             → Ignore unnecessary files
```

## 🌱 Future Enhancements

- Add Kafka UI (e.g., Kafdrop)
- Integrate logging with Loki or DataDog
- Container health checks and restart policies
- Kubernetes + Helm deployment (GKE or EKS)
- TLS & security hardening

## 👩‍💻 Author

**Vaishnavi K.**  
Master’s in Applied Data Science & Analytics  
Built with love, logic, and a stubborn Kafka broker.  
GitHub: https://github.com/vk20001


