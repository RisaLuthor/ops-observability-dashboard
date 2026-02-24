# Project Charter — Ops Observability Dashboard

## Why this exists
Enterprise services fail in predictable ways: latency spikes, dependency errors, bad deploys, noisy logs, and silent governance drift.
This project is a small, production-inspired dashboard that surfaces operational health and audit events in a way that supports review,
traceability, and fast incident triage.

## Goals (v1)
- Provide a lightweight operational dashboard for a FastAPI service
- Track request volume, errors, and latency trends per endpoint
- Capture audit/ops events with simple storage (SQLite) and retrieval
- Keep the system easy to run locally and via Docker

## Non-goals (v1)
- Full distributed tracing
- Multi-tenant RBAC
- Complex alert routing integrations (PagerDuty, etc.)

## Design constraints
- Deterministic, explainable outputs
- Safe-by-default logging (no secrets, no raw PII)
- Minimal external dependencies for MVP
- Clear separation between API and UI

## Definition of done (MVP)
- API exposes `/health`, `/metrics`, `/events`
- UI shows uptime, request/error counts, latency summary, and recent events
- Docker compose runs API + UI
- CI runs import smoke test + pytest (even if small)