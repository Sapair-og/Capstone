"""Append-only, timestamped event log. Every pipeline stage emits here (paper §IV-D)."""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_memory: list[dict[str, Any]] = []


def _path() -> Path | None:
    p = os.environ.get("LUCIDFORM_LOG")
    return Path(p) if p else None


def _jsonable(v: Any) -> Any:
    if hasattr(v, "to_dict"):
        return v.to_dict()
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    return v if isinstance(v, (str, int, float, bool, type(None))) else str(v)


def emit(kind: str, **data: Any) -> dict[str, Any]:
    ev = {"ts": time.time(), "kind": kind, **{k: _jsonable(v) for k, v in data.items()}}
    with _lock:
        _memory.append(ev)
        if (p := _path()) is not None:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def recent(kind: str | None = None) -> list[dict[str, Any]]:
    with _lock:
        return [e for e in _memory if kind is None or e["kind"] == kind]


def clear_memory() -> None:
    with _lock:
        _memory.clear()


def read_log(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
