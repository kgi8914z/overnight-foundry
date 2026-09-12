from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from common import ROOT, load_catalog

OUT = ROOT / "backlog" / "approvals.json"


def _prs(repo: str) -> list[dict]:
    try:
        raw = subprocess.check_output(
            ["gh", "pr", "list", "--repo", repo, "--state", "open", "--json", "number,title,url,isDraft"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        rows = json.loads(raw)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return []
    return [
        {
            "kind": "merge",
            "ref": f"#{row['number']}",
            "title": row.get("title"),
            "url": row.get("url"),
            "draft": bool(row.get("isDraft")),
        }
        for row in rows
    ]


def main() -> None:
    catalog = load_catalog()
    repo = f"{catalog['owner']}/{catalog['control_plane']}"
    waiting = _prs(repo)
    for asset in catalog.get("assets", []):
        if asset.get("specimen") and asset.get("lifecycle") == "incubator":
            waiting.append(
                {
                    "kind": "hold",
                    "ref": asset.get("id"),
                    "title": f"{asset.get('id')} is a pipeline specimen — kill if it never grows a viewer/user",
                    "url": None,
                    "draft": False,
                }
            )
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "waiting": waiting,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"approvals: {len(waiting)} items")


if __name__ == "__main__":
    main()
