from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"
LEDGER_PATH = ROOT / "ledger" / "metrics.jsonl"
BRIEFING_DIR = ROOT / "briefing"
DATA_DIR = ROOT / "data"
DASHBOARD_PATH = ROOT / "dashboard" / "index.html"
SCOUT_PATH = ROOT / "backlog" / "candidates.json"


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def kst_today() -> str:
    # UTC+9 without depending on zoneinfo data being present.
    return (datetime.now(timezone.utc).replace(tzinfo=None)).isoformat()


def today_stamp() -> str:
    return date.today().isoformat()


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def save_catalog(catalog: dict[str, Any]) -> None:
    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def live_assets(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in catalog.get("assets", []) if a.get("status") == "live"]


def counted_live(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in live_assets(catalog) if a.get("lane") in {"revive", "watch"}]


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
