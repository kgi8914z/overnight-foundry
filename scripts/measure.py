from __future__ import annotations

from datetime import datetime, timezone

from common import ROOT, count_jsonl, load_catalog, save_catalog, today_stamp


def main() -> None:
    catalog = load_catalog()
    now = datetime.now(timezone.utc).isoformat()
    for asset in catalog.get("assets", []):
        metrics = asset.setdefault("metrics", {})
        path = asset.get("data_path")
        if path:
            metrics["dataset_records"] = count_jsonl(ROOT / path)
        asset["last_measured_at"] = now
    catalog["measured_on"] = today_stamp()
    save_catalog(catalog)
    print("measure: catalog metrics refreshed from files")


if __name__ == "__main__":
    main()
