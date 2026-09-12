from __future__ import annotations

import html
import json
from pathlib import Path

from common import (
    DASHBOARD_PATH,
    LEDGER_PATH,
    ROOT,
    SCOUT_PATH,
    count_jsonl,
    load_catalog,
    read_jsonl,
)

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Overnight Foundry</title>
  <style>
    :root {{
      --bg: #111114;
      --fg: #ececec;
      --muted: #9a9aa3;
      --line: #2a2a30;
      --card: #1a1a1f;
      --accent: #7aa2ff;
      --good: #7dcea0;
      --warn: #e2b76b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font: 15px/1.5 ui-sans-serif, system-ui, sans-serif;
      background: var(--bg);
      color: var(--fg);
    }}
    main {{ max-width: 960px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1 {{ font-size: 24px; font-weight: 650; margin: 0 0 6px; }}
    .sub {{ color: var(--muted); margin-bottom: 28px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    @media (max-width: 720px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .stat {{ background: var(--card); border: 1px solid var(--line); padding: 14px 16px; }}
    .stat b {{ display: block; font-size: 28px; letter-spacing: -0.03em; }}
    .stat span {{ color: var(--muted); font-size: 12px; }}
    h2 {{ font-size: 16px; margin: 32px 0 10px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 550; }}
    a {{ color: var(--accent); text-decoration: none; }}
    .ok {{ color: var(--good); }}
    .hold {{ color: var(--warn); }}
    pre {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 14px 16px;
      white-space: pre-wrap;
      font: 13px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    footer {{ color: var(--muted); font-size: 12px; margin-top: 36px; }}
  </style>
</head>
<body>
<main>
  <h1>Overnight Foundry</h1>
  <p class="sub">밤 교대가 쌓은 것 · 갱신 {generated} · 테마 revive + watch · 살아 있는 상한 {live_cap}</p>
  <div class="grid">
    <div class="stat"><b>{apps}</b><span>Apps (theme live)</span></div>
    <div class="stat"><b>{datasets}</b><span>Datasets</span></div>
    <div class="stat"><b>{dataset_rows}</b><span>Dataset rows</span></div>
    <div class="stat"><b>{stars}</b><span>GitHub stars</span></div>
    <div class="stat"><b>{users}</b><span>Users</span></div>
    <div class="stat"><b>${mrr}</b><span>MRR</span></div>
  </div>
  <h2>Assets</h2>
  <table>
    <thead><tr><th>ID</th><th>Lane</th><th>Status</th><th>Users</th><th>Stars</th><th>Notes</th></tr></thead>
    <tbody>{asset_rows}</tbody>
  </table>
  <h2 id="pypi">PyPI updates (latest 50)</h2>
  <table>
    <thead><tr><th>Package</th><th>Published</th></tr></thead>
    <tbody>{pypi_rows}</tbody>
  </table>
  <h2>Revive candidates</h2>
  <table>
    <thead><tr><th>Name</th><th>Stars</th><th>Why look</th></tr></thead>
    <tbody>{candidate_rows}</tbody>
  </table>
  <h2>Latest briefing</h2>
  <pre>{brief}</pre>
  <footer>Source: catalog.json + ledger/metrics.jsonl + this generate step. 숫자는 공장 장부이지 외부 분석 제품이 아니다.</footer>
</main>
</body>
</html>
"""


def _cells(asset: dict) -> str:
    status = html.escape(str(asset.get("status", "")))
    klass = "ok" if asset.get("status") == "live" else "hold"
    return (
        f"<tr><td>{html.escape(str(asset.get('id', '')))}</td>"
        f"<td>{html.escape(str(asset.get('lane', '')))}</td>"
        f"<td class=\"{klass}\">{status}</td>"
        f"<td>{html.escape(str(asset.get('users', 0)))}</td>"
        f"<td>{html.escape(str(asset.get('stars', 0)))}</td>"
        f"<td>{html.escape(str(asset.get('notes', '')))}</td></tr>"
    )


def main() -> None:
    catalog = load_catalog()
    ledger = read_jsonl(LEDGER_PATH)
    snap = ledger[-1] if ledger else {}
    briefing = Path(__file__).resolve().parents[1] / "briefing" / "LATEST.md"
    brief = briefing.read_text(encoding="utf-8") if briefing.exists() else "아직 브리핑 없음"
    candidates = []
    if SCOUT_PATH.exists():
        candidates = json.loads(SCOUT_PATH.read_text(encoding="utf-8")).get("candidates", [])
    if not candidates:
        candidate_rows = "<tr><td colspan='3'>아직 없음</td></tr>"
    else:
        candidate_rows = "".join(
            f"<tr><td><a href=\"{html.escape(str(c.get('url', '')))}\">{html.escape(str(c.get('name', '')))}</a></td>"
            f"<td>{html.escape(str(c.get('stars', 0)))}</td>"
            f"<td>{html.escape(str(c.get('description', '')))}</td></tr>"
            for c in candidates
        )
    rows = 0
    for asset in catalog.get("assets", []):
        if asset.get("data_path"):
            rows += count_jsonl(ROOT / asset["data_path"])
    pypi = read_jsonl(ROOT / "data" / "watches" / "pypi-updates.jsonl")
    pypi_recent = list(reversed(pypi[-50:]))
    if not pypi_recent:
        pypi_rows = "<tr><td colspan='2'>아직 없음</td></tr>"
    else:
        pypi_rows = "".join(
            f"<tr><td><a href=\"{html.escape(str(item.get('link', '')))}\">{html.escape(str(item.get('title', '')))}</a></td>"
            f"<td>{html.escape(str(item.get('published', '')))}</td></tr>"
            for item in pypi_recent
        )
    html_out = TEMPLATE.format(
        generated=html.escape(str(snap.get("date") or "n/a")),
        live_cap=catalog.get("live_cap"),
        apps=snap.get("apps", 0),
        datasets=snap.get("datasets", 0),
        dataset_rows=snap.get("dataset_rows", rows),
        stars=snap.get("stars", 0),
        users=snap.get("users", 0),
        mrr=snap.get("mrr_usd", 0),
        asset_rows="".join(_cells(a) for a in catalog.get("assets", [])),
        candidate_rows=candidate_rows,
        pypi_rows=pypi_rows,
        brief=html.escape(brief),
    )
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(html_out, encoding="utf-8")
    print(f"dashboard: wrote {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()
