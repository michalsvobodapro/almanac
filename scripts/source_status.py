"""Persist source statuses to data/source-status.json (consumed by /sources page)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from models import SourceStatusEntry


REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = REPO_ROOT / "data" / "source-status.json"


def write_statuses(statuses: list[SourceStatusEntry]) -> None:
    payload = {
        "lastRunAt": datetime.now(timezone.utc).isoformat(),
        "sources": [s.model_dump(mode="json", exclude_none=True) for s in statuses],
    }
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(payload, indent=2, sort_keys=False, default=str))
