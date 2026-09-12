from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from common import ROOT, count_jsonl

SAVE_PATH = ROOT / "game" / "save.json"

TITLES = [
    (1, "견습 기록관"),
    (3, "밤길 수집가"),
    (5, "길드 서기"),
    (7, "유물 사냥꾼"),
    (9, "주조소 반장"),
    (12, "부활술사"),
    (16, "버려진 코드의 대마법사"),
]


def _title(level: int) -> str:
    name = TITLES[0][1]
    for need, label in TITLES:
        if level >= need:
            name = label
    return name


def _rarity(asset: dict[str, Any], rows: int) -> str:
    lane = asset.get("lane")
    if lane == "ops":
        return "본거지"
    if lane == "revive":
        return "유물"
    if rows >= 1000:
        return "희귀"
    if rows >= 100:
        return "고급"
    return "일반"


def xp_parts(catalog: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, int]:
    snap = ledger[-1] if ledger else {}
    rows = int(snap.get("dataset_rows") or 0)
    if not rows:
        for asset in catalog.get("assets", []):
            if asset.get("data_path"):
                rows += count_jsonl(ROOT / asset["data_path"])
    nights = len({row.get("date") for row in ledger if row.get("date")})
    theme_live = sum(
        1
        for a in catalog.get("assets", [])
        if a.get("status") == "live" and a.get("lane") in {"revive", "watch"}
    )
    stars = int(snap.get("stars") or 0)
    users = int(snap.get("users") or 0)
    mrr = float(snap.get("mrr_usd") or 0)
    return {
        "rows": rows * 2,
        "nights": nights * 50,
        "holdings": theme_live * 200,
        "renown": stars * 250,
        "followers": users * 100,
        "gold": int(mrr * 20),
    }


def level_from_xp(xp: int) -> tuple[int, int, int]:
    level = 1
    spent = 0
    while True:
        need = 120 * level
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
    row_gain = int(last.get("dataset_rows") or 0) - int(prev.get("dataset_rows") or 0)
    inventory = []
    for asset in catalog.get("assets", []):
        path = asset.get("data_path")
        rows = count_jsonl(ROOT / path) if path else 0
        inventory.append(
            {
                "id": asset.get("id"),
                "name": asset.get("name"),
                "lane": asset.get("lane"),
                "status": asset.get("status"),
                "rarity": _rarity(asset, rows),
                "stack": rows or int(asset.get("users") or 0),
                "notes": asset.get("notes") or "",
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
        "inventory": inventory,
        "loot": loot[:12],
    }


def write_save(save: dict[str, Any]) -> None:
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PATH.write_text(json.dumps(save, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
