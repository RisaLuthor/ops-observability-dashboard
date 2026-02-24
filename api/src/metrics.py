cat > api/src/metrics.py <<'PY'
import time
from collections import defaultdict
from typing import Dict

class MetricsStore:
    def __init__(self):
        self.start_time = time.time()
        self.requests_total = 0
        self.errors_total = 0
        self.by_status = defaultdict(int)
        self.by_route = defaultdict(lambda: {"count": 0, "errors": 0, "total_latency_ms": 0.0})

    def record(self, route: str, method: str, status_code: int, latency_ms: float):
        key = f"{method} {route}"

        self.requests_total += 1
        self.by_status[str(status_code)] += 1

        stats = self.by_route[key]
        stats["count"] += 1
        stats["total_latency_ms"] += latency_ms

        if status_code >= 400:
            self.errors_total += 1
            stats["errors"] += 1

    def snapshot(self) -> Dict:
        uptime = int(time.time() - self.start_time)

        routes = []
        for key, stats in self.by_route.items():
            method, route = key.split(" ", 1)
            avg_ms = stats["total_latency_ms"] / stats["count"] if stats["count"] else 0.0
            routes.append({
                "route": route,
                "method": method,
                "count": stats["count"],
                "errors": stats["errors"],
                "avg_ms": round(avg_ms, 2),
            })

        return {
            "service": "ops-observability-dashboard",
            "uptime_seconds": uptime,
            "requests_total": self.requests_total,
            "errors_total": self.errors_total,
            "by_status": dict(self.by_status),
            "by_route": routes,
        }

metrics_store = MetricsStore()
PY