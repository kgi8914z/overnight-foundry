from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from common import SCOUT_PATH

QUERY = "archived:true license:mit stars:>=200 pushed:<2024-01-01"


def gh_search() -> list[dict]:
    cmd = [
        "gh",
        "search",
        "repos",
        "--archived=true",
        "--stars",
        ">=200",
        "--license",
        "mit",
        "--updated",
        "<2024-01-01",
        "--sort",
        "stars",
        "--order",
        "desc",
        "--limit",
        "10",
        "--json",
        "name,url,stargazersCount,updatedAt,description,fullName,license,isArchived",
    ]
    try:
        raw = subprocess.check_output(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.STDOUT,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        SCOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "queried_at": datetime.now(timezone.utc).isoformat(),
            "query": QUERY,
            "error": str(exc),
            "candidates": [],
        }
        SCOUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"scout: gh failed, wrote empty candidate list ({exc})")
        return []
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError:
        rows = []
    skip_bits = ("awesome", "free-programming", "build-your-own", "interview")
    candidates = []
    for row in rows:
        name = (row.get("fullName") or row.get("name") or "").lower()
        desc = (row.get("description") or "").lower()
        stars = int(row.get("stargazersCount") or 0)
        if not row.get("isArchived"):
            continue
        if stars > 20000:
            continue
        if any(bit in name or bit in desc for bit in skip_bits):
            continue
        candidates.append(
            {
                "name": row.get("fullName") or row.get("name"),
                "url": row.get("url"),
                "stars": stars,
                "updatedAt": row.get("updatedAt"),
                "license": (row.get("license") or {}).get("key")
                if isinstance(row.get("license"), dict)
                else row.get("license"),
                "archived": row.get("isArchived"),
                "description": (row.get("description") or "")[:240],
                "lane": "revive",
            }
        )
    return candidates


def main() -> None:
    candidates = gh_search()
    payload = {
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "query": QUERY,
        "candidates": candidates[:5],
    }
    SCOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCOUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"scout: wrote {len(payload['candidates'])} revive candidates")


if __name__ == "__main__":
    main()
