from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from common import (
    BRIEFING_DIR,
    LEDGER_PATH,
    SCOUT_PATH,
    append_jsonl,
    counted_live,
    count_jsonl,
    live_assets,
    load_catalog,
    read_jsonl,
    today_stamp,
)


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
                "title,url,isDraft",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        rows = json.loads(raw)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return []
    return [f"- {row['title']} — {row['url']}" for row in rows if row.get("isDraft") or True]


def dataset_rows(catalog: dict) -> int:
    total = 0
    for asset in catalog.get("assets", []):
        path = asset.get("data_path")
        if path:
            total += count_jsonl(Path(__file__).resolve().parents[1] / path)
    return total


def main() -> None:
    catalog = load_catalog()
    owner_repo = f"{catalog['owner']}/{catalog['control_plane']}"
    stars = repo_stars(owner_repo)
    rows = dataset_rows(catalog)
    live = counted_live(catalog)
    users = sum(int(a.get("users") or 0) for a in live_assets(catalog))
    mrr = sum(float(a.get("mrr_usd") or 0) for a in live_assets(catalog))
    workflows = 2
    candidates = []
    if SCOUT_PATH.exists():
        candidates = json.loads(SCOUT_PATH.read_text(encoding="utf-8")).get("candidates", [])

    snapshot = {
        "date": today_stamp(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "apps": len(live),
        "datasets": sum(1 for a in live if a.get("kind") == "dataset"),
        "dataset_rows": rows,
        "stars": stars,
        "users": users,
        "mrr_usd": mrr,
        "workflows": workflows,
        "kill_candidates": 0,
    }
    previous = read_jsonl(LEDGER_PATH)
    last = previous[-1] if previous else {}
    append_jsonl(LEDGER_PATH, snapshot)

    def delta(key: str) -> str:
        now = snapshot.get(key, 0)
        was = last.get(key, 0)
        try:
            diff = now - was
        except TypeError:
            return str(now)
        sign = "+" if diff > 0 else ""
        return f"{now} ({sign}{diff})"

    pr_lines = open_draft_prs(owner_repo)
    cand_lines = [
        f"- {c.get('name')} ({c.get('stars')}★) {c.get('url')}"
        for c in candidates[:5]
    ]

    body = "\n".join(
        [
            f"# Morning brief {snapshot['date']}",
            "",
            "## Decide",
            *(pr_lines or ["- no open PRs"]),
            "",
            "## Grew overnight",
            f"- live theme assets: {delta('apps')}",
            f"- datasets: {delta('datasets')}",
            f"- dataset rows: {delta('dataset_rows')}",
            f"- stars: {delta('stars')}",
            f"- users: {delta('users')}",
            f"- mrr: ${snapshot['mrr_usd']}",
            f"- workflows: {snapshot['workflows']}",
            "",
            "## Revive candidates",
            *(cand_lines or ["- none yet"]),
            "",
            "## Kill candidates",
            "- none",
            "",
            "Reply: merge / hold / kill.",
            "",
        ]
    )
    BRIEFING_DIR.mkdir(parents=True, exist_ok=True)
    out = BRIEFING_DIR / f"{snapshot['date']}.md"
    out.write_text(body, encoding="utf-8")
    latest = BRIEFING_DIR / "LATEST.md"
    latest.write_text(body, encoding="utf-8")
    print(f"brief: wrote {out}")


if __name__ == "__main__":
    main()
