import os
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from .events_store import event_store

router = APIRouter()


Level = Literal["INFO", "WARN", "ERROR"]
Type = Literal["AUDIT", "OPS", "SECURITY", "DEPLOY"]


class EventIn(BaseModel):
    level: Level = "INFO"
    type: Type = "OPS"
    service: str = Field(default="api", min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1000)
    meta: Dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    id: str
    ts: str
    level: str
    service: str
    message: str
    meta: Dict[str, Any]


def require_token(x_ops_token: Optional[str] = Header(default=None)) -> None:
    expected = os.getenv("OPS_API_TOKEN")
    if not expected:
        # If no token is set, we fail closed (safer when ports are public).
        raise HTTPException(status_code=503, detail="Server token not configured.")
    if not x_ops_token or x_ops_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized.")


@router.get("/events", response_model=List[EventOut])
def get_events(limit: int = 50, level: Optional[str] = None, service: Optional[str] = None):
    return event_store.list_events(limit=limit, level=level, service=service)


@router.get("/events/summary")
def get_events_summary():
    return event_store.summary()


@router.post("/events", response_model=EventOut, dependencies=[Depends(require_token)])
def post_event(event: EventIn):
    # Force meta to include type for easy filtering later
    meta = dict(event.meta or {})
    meta.setdefault("type", event.type)

    created = event_store.add_event(
        level=event.level,
        service=event.service,
        message=event.message,
        meta=meta,
    )
    return created
