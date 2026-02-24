import time
from fastapi import FastAPI, Request

from .metrics import metrics_store
from .events_api import router as events_router

app = FastAPI(title="Ops Observability Dashboard API", version="0.2.0")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency_ms = (time.time() - start) * 1000
    metrics_store.record(
        route=request.url.path,
        method=request.method,
        status_code=response.status_code,
        latency_ms=latency_ms,
    )
    return response

@app.get("/")
def root():
    return {"service": "ops-observability-dashboard", "status": "ok"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/metrics")
def metrics():
    return metrics_store.snapshot()

app.include_router(events_router)
