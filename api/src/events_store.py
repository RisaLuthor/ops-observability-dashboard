import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

DEFAULT_DB_PATH = os.getenv("EVENTS_DB_PATH", "data/events.db")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventStore:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    ts TEXT NOT NULL,
                    level TEXT NOT NULL,
                    service TEXT NOT NULL,
                    message TEXT NOT NULL,
                    meta_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_level ON events(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_service ON events(service)")

    def add_event(
        self,
        level: str,
        service: str,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event_id = str(uuid4())
        ts = _utc_now_iso()
        meta_json = json.dumps(meta or {}, ensure_ascii=False)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (id, ts, level, service, message, meta_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (event_id, ts, level, service, message, meta_json),
            )

        return {
            "id": event_id,
            "ts": ts,
            "level": level,
            "service": service,
            "message": message,
            "meta": meta or {},
        }

    def list_events(
        self,
        limit: int = 50,
        level: Optional[str] = None,
        service: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 500))

        clauses = []
        params: List[Any] = []

        if level:
            clauses.append("level = ?")
            params.append(level)
        if service:
            clauses.append("service = ?")
            params.append(service)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        sql = f"""
            SELECT id, ts, level, service, message, meta_json
            FROM events
            {where_sql}
            ORDER BY ts DESC
            LIMIT ?
        """
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "id": r["id"],
                    "ts": r["ts"],
                    "level": r["level"],
                    "service": r["service"],
                    "message": r["message"],
                    "meta": json.loads(r["meta_json"] or "{}"),
                }
            )
        return out

    def summary(self) -> Dict[str, Any]:
        with self._connect() as conn:
            by_level = conn.execute(
                "SELECT level, COUNT(*) AS c FROM events GROUP BY level"
            ).fetchall()
            by_service = conn.execute(
                "SELECT service, COUNT(*) AS c FROM events GROUP BY service"
            ).fetchall()

        return {
            "by_level": {r["level"]: r["c"] for r in by_level},
            "by_service": {r["service"]: r["c"] for r in by_service},
        }


event_store = EventStore()
