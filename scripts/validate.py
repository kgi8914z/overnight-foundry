from __future__ import annotations

import sys

from common import CATALOG_PATH, counted_live, load_catalog

REQUIRED_ASSET = {"id", "name", "lane", "status", "repo"}
LANES = {"revive", "watch", "ops"}
STATUSES = {"live", "draft", "archived", "kill-candidate"}


def main() -> int:
    catalog = load_catalog()
    errors: list[str] = []
    if catalog.get("version") != 1:
        errors.append("catalog.version must be 1")
    if not catalog.get("owner"):
        errors.append("catalog.owner missing")
    ids: set[str] = set()
    for i, asset in enumerate(catalog.get("assets", [])):
        missing = REQUIRED_ASSET - set(asset)
        if missing:
            errors.append(f"assets[{i}] missing {sorted(missing)}")
        if asset.get("lane") not in LANES:
            errors.append(f"assets[{i}].lane invalid: {asset.get('lane')}")
        if asset.get("status") not in STATUSES:
            errors.append(f"assets[{i}].status invalid: {asset.get('status')}")
        if asset.get("id") in ids:
            errors.append(f"duplicate id {asset.get('id')}")
        ids.add(asset.get("id"))
    live = counted_live(catalog)
    cap = int(catalog.get("live_cap") or 0)
    if len(live) > cap:
        errors.append(f"live theme assets {len(live)} exceed live_cap {cap}")
    if errors:
        print(f"{CATALOG_PATH} invalid:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"catalog ok: {len(catalog.get('assets', []))} assets, {len(live)} live")
    return 0


if __name__ == "__main__":
    sys.exit(main())
