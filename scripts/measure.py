from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import ROOT, count_jsonl, load_catalog, save_catalog, today_stamp, read_jsonl
from xp import apply_measurement

EVENTS_DIR = ROOT / "data" / "events"


def _event_rows() -> list[dict]:
    if not EVENTS_DIR.exists():
        return []
    rows: list[dict] = []
    for path in sorted(EVENTS_DIR.glob("*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def _parse_at(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def apply_events(catalog: dict) -> None:
    now = datetime.now(timezone.utc)
    day = now.date()
    week = now - timedelta(days=7)
    by_asset: dict[str, list[dict]] = defaultdict(list)
    for row in _event_rows():
        by_asset[str(row.get("asset") or "foundry")].append(row)

    for asset in catalog.get("assets", []):
        metrics = asset.setdefault("metrics", {})
        rows = by_asset.get(str(asset.get("id")), [])
        vids = {r.get("vid") for r in rows if r.get("vid")}
        day_vids = set()
        week_self = 0
        api = 0
        for row in rows:
            when = _parse_at(str(row.get("at") or ""))
            kind = row.get("type")
            if kind == "api_call":
                api += 1
            if when and when.date() == day and row.get("vid"):
                day_vids.add(row.get("vid"))
            if kind == "self_use" and when and when >= week:
                week_self += 1
        if vids:
            metrics["unique_users"] = max(int(metrics.get("unique_users") or 0), len(vids))
        metrics["active_users_1d"] = len(day_vids)
        metrics["self_uses_weekly"] = week_self
        if api:
            metrics["api_calls"] = api


def main() -> None:
    catalog = load_catalog()
    now = datetime.now(timezone.utc).isoformat()
    for asset in catalog.get("assets", []):
        metrics = asset.setdefault("metrics", {})
        path = asset.get("data_path")
        if path:
            metrics["dataset_records"] = count_jsonl(ROOT / path)
        asset["last_measured_at"] = now
    apply_events(catalog)
    catalog["measured_on"] = today_stamp()
    save_catalog(catalog)
    result = apply_measurement(catalog, date=today_stamp(), night_shift_ok=True)
    init = "cursor-init" if result["initialized"] else f"awards={len(result['awards'])}"
    print(f"measure: catalog refreshed, xp {init}, total={result['total_xp']}")


if __name__ == "__main__":
    main()
