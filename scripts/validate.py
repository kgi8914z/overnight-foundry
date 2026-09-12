from __future__ import annotations

import sys

from common import (
    CATALOG_PATH,
    LANES,
    LIFECYCLES,
    load_catalog,
    load_config,
    slot_counts,
)

REQUIRED_ASSET = {"id", "name", "lane", "lifecycle", "repo", "problem", "mvp", "kill"}


def main() -> int:
    catalog = load_catalog()
    config = load_config()
    errors: list[str] = []
    if catalog.get("version") != 2:
        errors.append("catalog.version must be 2")
    if not catalog.get("owner"):
        errors.append("catalog.owner missing")
    ids: set[str] = set()
    for i, asset in enumerate(catalog.get("assets", [])):
        missing = REQUIRED_ASSET - set(asset)
        if missing:
            errors.append(f"assets[{i}] missing {sorted(missing)}")
        if asset.get("lane") not in LANES:
            errors.append(f"assets[{i}].lane invalid: {asset.get('lane')}")
        if asset.get("lifecycle") not in LIFECYCLES:
            errors.append(f"assets[{i}].lifecycle invalid: {asset.get('lifecycle')}")
        if asset.get("lane") == "revive":
            errors.append("revive lane is forbidden in v2")
        if asset.get("id") in ids:
            errors.append(f"duplicate id {asset.get('id')}")
        ids.add(asset.get("id"))
        if "metrics" not in asset:
            errors.append(f"assets[{i}] missing metrics")
    counts = slot_counts(catalog)
    slots = config.get("slots") or {}
    for bucket, used in counts.items():
        cap = int(slots.get(bucket) or 0)
        if used > cap:
            errors.append(f"{bucket} {used} exceeds cap {cap}")
    if errors:
        print(f"{CATALOG_PATH} invalid:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"catalog ok: {len(catalog.get('assets', []))} assets, slots {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
