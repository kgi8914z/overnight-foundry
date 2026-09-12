from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import ROOT, load_config, read_jsonl, append_jsonl

XP_LEDGER = ROOT / "ledger" / "xp.jsonl"
XP_CURSOR = ROOT / "ledger" / "xp_cursor.json"

USER_DELTA_ORDER = (
    "repeat_users",
    "paying_users",
    "unique_users",
    "active_users_1d",
    "self_uses_weekly",
    "backlinks",
    "stars",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_cursor() -> dict[str, Any]:
    if not XP_CURSOR.exists():
        return {"metrics": {}, "dataset_milestones_hit": {}, "night_dates": [], "total_xp": 0}
    return json.loads(XP_CURSOR.read_text(encoding="utf-8"))


def save_cursor(cursor: dict[str, Any]) -> None:
    XP_CURSOR.parent.mkdir(parents=True, exist_ok=True)
    XP_CURSOR.write_text(json.dumps(cursor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def total_xp_from_ledger(path: Path = XP_LEDGER) -> int:
    return sum(int(row.get("xp") or 0) for row in read_jsonl(path))


def level_from_xp(xp: int, step: int = 150) -> tuple[int, int, int]:
    level = 1
    spent = 0
    while True:
        need = step * level
        if xp < spent + need:
            return level, xp - spent, need
        spent += need
        level += 1


def dataset_growth_xp(new_records: int, log2_weight: int) -> int:
    if new_records <= 0:
        return 0
    return int(log2_weight * math.log2(1 + new_records))


def api_calls_xp(new_calls: int, log2_weight: int) -> int:
    if new_calls <= 0:
        return 0
    return int(log2_weight * math.log2(1 + new_calls))


def crossed_milestones(prev: int, curr: int, marks: list[int]) -> list[int]:
    return [mark for mark in marks if prev < mark <= curr]


def awards_for_asset(
    asset_id: str,
    prev: dict[str, int],
    curr: dict[str, int],
    config: dict[str, Any],
    already_hit: list[int],
) -> list[dict[str, Any]]:
    xp_cfg = config.get("xp") or {}
    delta_w = xp_cfg.get("delta") or {}
    ds_cfg = xp_cfg.get("dataset") or {}
    awards: list[dict[str, Any]] = []

    for key in USER_DELTA_ORDER:
        gain = int(curr.get(key) or 0) - int(prev.get(key) or 0)
        if gain <= 0:
            continue
        awards.append(
            {
                "asset": asset_id,
                "reason": key,
                "delta": gain,
                "xp": gain * int(delta_w.get(key) or 0),
            }
        )

    api_gain = int(curr.get("api_calls") or 0) - int(prev.get("api_calls") or 0)
    api_xp = api_calls_xp(api_gain, int(xp_cfg.get("api_calls_log2") or 0))
    if api_xp:
        awards.append({"asset": asset_id, "reason": "api_calls", "delta": api_gain, "xp": api_xp})

    rec_prev = int(prev.get("dataset_records") or 0)
    rec_curr = int(curr.get("dataset_records") or 0)
    rec_gain = rec_curr - rec_prev
    growth = dataset_growth_xp(rec_gain, int(ds_cfg.get("log2_weight") or 0))
    if growth:
        awards.append(
            {"asset": asset_id, "reason": "dataset_log2", "delta": rec_gain, "xp": growth}
        )
    marks = [int(m) for m in ds_cfg.get("milestones") or []]
    hit = crossed_milestones(rec_prev, rec_curr, marks)
    new_marks = [m for m in hit if m not in already_hit]
    if new_marks:
        awards.append(
            {
                "asset": asset_id,
                "reason": "dataset_milestone",
                "delta": rec_curr,
                "xp": int(ds_cfg.get("milestone_xp") or 0) * len(new_marks),
                "milestones": new_marks,
            }
        )
    return awards


def apply_measurement(
    catalog: dict[str, Any],
    *,
    date: str,
    night_shift_ok: bool = False,
    initialize_only: bool | None = None,
) -> dict[str, Any]:
    """Award XP from metric deltas since the last cursor. Never recomputes from totals."""
    config = load_config()
    cursor = load_cursor()
    prev_metrics: dict[str, dict[str, int]] = cursor.get("metrics") or {}
    milestones = cursor.get("dataset_milestones_hit") or {}
    night_dates = list(cursor.get("night_dates") or [])
    first_run = not prev_metrics
    if initialize_only is None:
        initialize_only = first_run

    all_awards: list[dict[str, Any]] = []
    next_metrics: dict[str, dict[str, int]] = {}
    next_marks: dict[str, list[int]] = dict(milestones)

    for asset in catalog.get("assets", []):
        asset_id = str(asset.get("id"))
        curr = {k: int(v or 0) for k, v in (asset.get("metrics") or {}).items()}
        next_metrics[asset_id] = curr
        if initialize_only:
            rec = int(curr.get("dataset_records") or 0)
            next_marks[asset_id] = [m for m in (config.get("xp") or {}).get("dataset", {}).get("milestones", []) if rec >= int(m)]
            continue
        prev = prev_metrics.get(asset_id) or {}
        hit = list(milestones.get(asset_id) or [])
        for award in awards_for_asset(asset_id, prev, curr, config, hit):
            all_awards.append(award)
            if award["reason"] == "dataset_milestone":
                hit = sorted(set(hit) | set(award.get("milestones") or []))
        next_marks[asset_id] = hit

    if night_shift_ok and date not in night_dates and not initialize_only:
        all_awards.append(
            {
                "asset": "foundry",
                "reason": "night_shift_success",
                "delta": 1,
                "xp": int((config.get("xp") or {}).get("night_shift_success") or 0),
            }
        )
        night_dates.append(date)

    at = _now()
    for award in all_awards:
        if int(award.get("xp") or 0) <= 0:
            continue
        append_jsonl(
            XP_LEDGER,
            {"at": at, "date": date, **award},
        )

    total = total_xp_from_ledger()
    cursor = {
        "metrics": next_metrics,
        "dataset_milestones_hit": next_marks,
        "night_dates": night_dates,
        "total_xp": total,
        "updated_at": at,
        "initialized": True,
    }
    save_cursor(cursor)
    return {"awards": all_awards, "total_xp": total, "initialized": initialize_only}
