from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from common import (
    BRIEFING_DIR,
    LEDGER_PATH,
    SCOUT_PATH,
    append_jsonl,
    counted_live,
    live_assets,
    load_catalog,
    metric_sum,
    read_jsonl,
    slot_counts,
    today_stamp,
)
from game import build_save


def repo_stars(repo: str) -> int:
    try:
        raw = subprocess.check_output(
            ["gh", "repo", "view", repo, "--json", "stargazerCount"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        return int(json.loads(raw).get("stargazerCount") or 0)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return 0


def open_draft_prs(repo: str) -> list[str]:
    try:
        raw = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "open",
                "--json",
                "number,title,url",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        rows = json.loads(raw)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return []
    return [f"- Merge PR #{row['number']}: {row['title']} — {row['url']}" for row in rows]


def main() -> None:
    catalog = load_catalog()
    owner_repo = f"{catalog['owner']}/{catalog['control_plane']}"
    stars = repo_stars(owner_repo)
    for asset in catalog.get("assets", []):
        if asset.get("id") == "foundry":
            asset.setdefault("metrics", {})["stars"] = stars
    records = metric_sum(catalog, "dataset_records")
    snapshot = {
        "date": today_stamp(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "active_assets": len(live_assets(catalog)),
        "slotted": len(counted_live(catalog)),
        "slots": slot_counts(catalog),
        "dataset_records": records,
        "dataset_rows": records,
        "unique_users": metric_sum(catalog, "unique_users"),
        "repeat_users": metric_sum(catalog, "repeat_users"),
        "stars": stars,
        "mrr_usd": 0,
        "kill_candidates": 0,
    }
    previous = read_jsonl(LEDGER_PATH)
    last = previous[-1] if previous else {}
    append_jsonl(LEDGER_PATH, snapshot)

    def delta(key: str) -> str:
        now = snapshot.get(key, 0)
        was = last.get(key, 0)
        try:
            diff = int(now) - int(was)
        except (TypeError, ValueError):
            return str(now)
        sign = "+" if diff > 0 else ""
        return f"{now} ({sign}{diff})"

    pr_lines = open_draft_prs(owner_repo)
    candidates = []
    if SCOUT_PATH.exists():
        candidates = json.loads(SCOUT_PATH.read_text(encoding="utf-8")).get("candidates", [])
    cand_lines = [f"- {c.get('name')}: {c.get('description')}" for c in candidates[:5]]
    save = build_save(catalog, previous + [snapshot], [])
    remain = max(save["xp_for_level"] - save["xp_into_level"], 0)
    completed = [
        f"- {a.get('id')}: lifecycle={a.get('lifecycle')} records={(a.get('metrics') or {}).get('dataset_records', 0)}"
        for a in catalog.get("assets", [])
        if a.get("lifecycle") != "archived"
    ]
    body = "\n".join(
        [
            f"# OVERNIGHT REPORT {snapshot['date']}",
            "",
            f"{save['title']} Lv {save['level']} · XP {save['xp']} · 다음 레벨까지 {remain}",
            "",
            "## Completed",
            *(completed or ["- none"]),
            "",
            "## Waiting for approval",
            *(pr_lines or ["- none"]),
            "",
            "## Metrics",
            f"- Active assets: {snapshot['active_assets']}",
            f"- Slots incubator/growing/maintenance: {snapshot['slots']}",
            f"- Unique users: {snapshot['unique_users']}",
            f"- Repeat users: {snapshot['repeat_users']}",
            f"- Dataset records: {delta('dataset_records')}",
            f"- Stars (vanity): {snapshot['stars']}",
            f"- MRR: ${snapshot['mrr_usd']}",
            f"- XP: {save['xp']}",
            f"- Level: {save['level']}",
            "",
            "## Scout seeds",
            *(cand_lines or ["- none"]),
            "",
            "Decisions needed: MERGE / HOLD / KILL",
            "",
        ]
    )
    BRIEFING_DIR.mkdir(parents=True, exist_ok=True)
    out = BRIEFING_DIR / f"{snapshot['date']}.md"
    out.write_text(body, encoding="utf-8")
    (BRIEFING_DIR / "LATEST.md").write_text(body, encoding="utf-8")
    print(f"brief: wrote {out}")


if __name__ == "__main__":
    main()
