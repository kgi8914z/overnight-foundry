from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from common import ROOT, count_jsonl, live_assets, load_config, metric_sum

SAVE_PATH = ROOT / "game" / "save.json"

TITLES = [
    (1, "견습 길드장"),
    (3, "밤길 실험가"),
    (5, "측정하는 서기"),
    (7, "도태의 반장"),
    (9, "선택하는 주조공"),
    (12, "제국 회계관"),
    (16, "사용량의 대마법사"),
]


def _title(level: int) -> str:
    name = TITLES[0][1]
    for need, label in TITLES:
        if level >= need:
            name = label
    return name


def _rarity(asset: dict[str, Any], rows: int) -> str:
    life = asset.get("lifecycle")
    if asset.get("lane") == "ops":
        return "본거지"
    if life == "growing":
        return "성장"
    if life == "maintenance":
        return "유지"
    if rows >= 1000:
        return "희귀"
    if rows >= 100:
        return "고급"
    return "부화"


def xp_parts(catalog: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, int]:
    weights = (load_config().get("xp") or {})
    nights = len({row.get("date") for row in ledger if row.get("date")})
    keys = [
        "unique_users",
        "repeat_users",
        "active_users_1d",
        "api_calls",
        "dataset_records",
        "paying_users",
        "self_uses_weekly",
        "backlinks",
        "stars",
    ]
    parts = {key: metric_sum(catalog, key) * int(weights.get(key) or 0) for key in keys}
    parts["nights"] = nights * int(weights.get("nights") or 0)
    return parts


def level_from_xp(xp: int) -> tuple[int, int, int]:
    level = 1
    spent = 0
    while True:
        need = 150 * level
        if xp < spent + need:
            return level, xp - spent, need
        spent += need
        level += 1


def build_save(catalog: dict[str, Any], ledger: list[dict[str, Any]], loot: list[dict[str, Any]]) -> dict[str, Any]:
    parts = xp_parts(catalog, ledger)
    xp = sum(parts.values())
    level, into, need = level_from_xp(xp)
    prev = ledger[-2] if len(ledger) >= 2 else {}
    last = ledger[-1] if ledger else {}
    row_gain = int(last.get("dataset_records") or last.get("dataset_rows") or 0) - int(
        prev.get("dataset_records") or prev.get("dataset_rows") or 0
    )
    inventory = []
    for asset in catalog.get("assets", []):
        path = asset.get("data_path")
        rows = int((asset.get("metrics") or {}).get("dataset_records") or 0)
        if path and not rows:
            rows = count_jsonl(ROOT / path)
        inventory.append(
            {
                "id": asset.get("id"),
                "name": asset.get("name"),
                "lane": asset.get("lane"),
                "status": asset.get("lifecycle"),
                "rarity": _rarity(asset, rows),
                "stack": rows or int((asset.get("metrics") or {}).get("self_uses_weekly") or 0),
                "notes": asset.get("problem") or "",
            }
        )
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "hero": "kgi8914z",
        "guild": "Overnight Foundry",
        "level": level,
        "title": _title(level),
        "xp": xp,
        "xp_into_level": into,
        "xp_for_level": need,
        "xp_parts": parts,
        "row_gain": max(row_gain, 0),
        "nights": len({row.get("date") for row in ledger if row.get("date")}),
        "active_assets": len(live_assets(catalog)),
        "inventory": inventory,
        "loot": loot[:12],
    }


def write_save(save: dict[str, Any]) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PATH.write_text(json.dumps(save, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
