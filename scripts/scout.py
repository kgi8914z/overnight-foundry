from __future__ import annotations

import json
from datetime import datetime, timezone

from common import SCOUT_PATH, load_catalog, slot_counts, load_config

# Public, licensed-enough starting points. Not abandoned-repo resurrection.
SEEDS = [
    {
        "name": "foundry-dashboard",
        "lane": "ops",
        "url": "https://github.com/kgi8914z/overnight-foundry",
        "description": "Finish the independent morning dashboard before any new utility.",
    },
    {
        "name": "watch-pypi-viewer-in-app",
        "lane": "watch",
        "url": "https://pypi.org/rss/updates.xml",
        "description": "Move the PyPI loot panel into apps/web with measure hooks.",
    },
]


def main() -> None:
    catalog = load_catalog()
    config = load_config()
    used = slot_counts(catalog)["incubator"]
    cap = int((config.get("slots") or {}).get("incubator") or 0)
    note = "incubator has room" if used < cap else "incubator full — scout must not open a new asset"
    payload = {
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "query": "v2 utility/watch seeds — no revive",
        "note": note,
        "incubator_used": used,
        "incubator_cap": cap,
        "candidates": SEEDS if used < cap else SEEDS[:1],
    }
    SCOUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCOUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"scout: {len(payload['candidates'])} seeds ({note})")


if __name__ == "__main__":
    main()
