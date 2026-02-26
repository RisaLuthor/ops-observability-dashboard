# ops-observability-dashboard

![CI](https://github.com/RisaLuthor/ops-observability-dashboard/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-tracked-blue)

Production-inspired observability dashboard designed to model enterprise-grade service monitoring patterns, including API health tracking, request latency instrumentation, error visibility, metrics aggregation, and structured operational event logging.

---

## 📌 Engineering Intent

This project was designed as a systems-thinking exercise to simulate how modern backend services expose telemetry, operational signals, and runtime diagnostics in structured environments.

Rather than focusing on UI aesthetics, the emphasis is on **observability mechanics**, **service behavior visibility**, and **production-style instrumentation patterns**.

---

## 🚀 Key Capabilities

✔ Health monitoring endpoints  
✔ Latency instrumentation middleware  
✔ Metrics aggregation & snapshot API  
✔ Structured operational event ingestion  
✔ Token-protected operational routes  
✔ Deterministic test suite & CI pipeline  

---

## 🧱 Architecture Overview

The system models a simplified observability layer commonly found in enterprise services.

### **Request Flow**

Client Request
↓
Middleware Instrumentation
↓
Route Handler
↓
Metrics Store


### **Operational Signals Captured**

• Health state  
• Latency measurements  
• Response status codes  
• Structured events  

---

## 🔍 Observability Features

### **Latency Instrumentation**

All HTTP requests are intercepted via middleware to capture:

• Route path  
• HTTP method  
• Status code  
• Request latency (ms)

---

### **Metrics Snapshot API**

Aggregated metrics are exposed through:

```http
GET /metrics
```

### Example Response

```
{
  "requests": [
    {
      "route": "/health",
      "method": "GET",
      "status_code": 200,
      "latency_ms": 12.4
    },
    {
      "route": "/events",
      "method": "POST",
      "status_code": 200,
      "latency_ms": 48.9
    }
  ]
}
```

### **Health Monitoring
Basic service health indicators are available via:

```
GET /
GET /health
```

Example Response

```
{
  "ok": true
}
```

### **Structured Operational Events
Operational events can be ingested and queried:

```
POST /events
GET /events
```

Example Event Submission

```
{
  "level": "WARN",
  "type": "AUDIT",
  "service": "api",
  "message": "Unexpected latency spike detected",
  "meta": {
    "request_id": "abc123"
  }
}
```

Example Response

```
{
  "id": 1,
  "level": "WARN",
  "service": "api",
  "meta": {
    "type": "AUDIT",
    "request_id": "abc123"
  }
}
```

### 🔐 Security Model
Event ingestion endpoints require a token.

Header

```
X-Ops-Token: <token>
```

Environment Variable

```
OPS_API_TOKEN
```

### 🛠 Tech Stack
• FastAPI
• Python
• Pytest
• Ruff / Black / MyPy
• GitHub Actions CI
• Docker

### ▶ Running Locally
Install Dependencies

pip install -r api/requirements.txt


## **Start API

uvicorn api.src.main:app --reload


## **Health Check

curl http://127.0.0.1:8000/health

### 🧪 Running Tests

pytest


## **With coverage:

pytest --cov=api


### 📄 License
MIT License






