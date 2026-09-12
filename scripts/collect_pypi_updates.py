from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from common import DATA_DIR, append_jsonl, read_jsonl

FEED = "https://pypi.org/rss/updates.xml"
OUT = DATA_DIR / "watches" / "pypi-updates.jsonl"


def fetch_feed() -> str:
    req = Request(FEED, headers={"User-Agent": "overnight-foundry/0.1"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_items(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        guid = (item.findtext("guid") or link or title).strip()
        key = hashlib.sha1(guid.encode("utf-8")).hexdigest()[:16]
        items.append(
            {
                "id": key,
                "title": title,
                "link": link,
                "published": pub,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def main() -> None:
    existing = {row.get("id") for row in read_jsonl(OUT)}
    added = 0
    for item in parse_items(fetch_feed()):
        if item["id"] in existing:
            continue
        append_jsonl(OUT, item)
        existing.add(item["id"])
        added += 1
    print(f"pypi-updates: added {added}, total {len(existing)}")


if __name__ == "__main__":
    main()
