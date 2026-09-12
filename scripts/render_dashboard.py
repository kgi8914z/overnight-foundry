from __future__ import annotations

import html
import json

from common import LEDGER_PATH, ROOT, SCOUT_PATH, load_catalog, read_jsonl
from game import build_save, write_save

DASHBOARD = ROOT / "dashboard" / "index.html"

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Overnight Foundry — 길드 홀</title>
  <style>
    :root {{
      --bg: #16130f;
      --fg: #f3ead7;
      --muted: #a3947c;
      --line: #3a3228;
      --card: #221c16;
      --gold: #d4a24c;
      --xp: #c9842e;
      --good: #8fbe7a;
      --rare: #7ea0d6;
      --relic: #c97b4b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--fg);
      background: var(--bg);
      font: 15px/1.5 Georgia, "Iowan Old Style", "Palatino Linotype", serif;
    }}
    main {{ max-width: 980px; margin: 0 auto; padding: 28px 18px 72px; }}
    .kicker {{ color: var(--gold); letter-spacing: 0.14em; font-size: 11px; text-transform: uppercase; }}
    h1 {{ font-size: 30px; margin: 6px 0 4px; font-weight: 700; }}
    .sub {{ color: var(--muted); margin: 0 0 22px; }}
    .hero {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 20px 22px 18px;
    }}
    .row {{ display: flex; gap: 28px; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; }}
    .lvl {{ font-size: 42px; line-height: 1; color: var(--gold); }}
    .lvl span {{ display: block; font-size: 13px; color: var(--muted); margin-top: 4px; }}
    .bar-wrap {{ flex: 1; min-width: 220px; }}
    .bar {{ height: 14px; background: #2a241c; border: 1px solid var(--line); }}
    .bar > i {{ display: block; height: 100%; background: var(--xp); width: {xp_pct}%; }}
    .bar-label {{ margin-top: 6px; color: var(--muted); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 16px; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .stat {{ border: 1px solid var(--line); padding: 10px 12px; }}
    .stat b {{ display: block; font-size: 22px; color: var(--gold); }}
    .stat span {{ color: var(--muted); font-size: 12px; }}
    h2 {{ font-size: 17px; margin: 34px 0 10px; color: var(--gold); }}
    .cards {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    @media (max-width: 760px) {{ .cards {{ grid-template-columns: 1fr; }} }}
    .item {{ background: var(--card); border: 1px solid var(--line); padding: 12px 14px; }}
    .tag {{ font-size: 11px; letter-spacing: 0.08em; color: var(--muted); }}
    .tag.고급 {{ color: var(--good); }}
    .tag.희귀 {{ color: var(--rare); }}
    .tag.유물 {{ color: var(--relic); }}
    .stack {{ float: right; color: var(--gold); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 7px 6px; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--muted); font-weight: 550; }}
    a {{ color: #e6c27a; text-decoration: none; }}
    footer {{ color: var(--muted); font-size: 12px; margin-top: 40px; }}
  </style>
</head>
<body>
<main>
  <div class="kicker">Night Shift Campaign</div>
  <h1>{title}</h1>
  <p class="sub">{guild} · {hero} · {nights}일째 원정 · 저장 {generated}</p>

  <section class="hero">
    <div class="row">
      <div class="lvl">Lv {level}<span>{title}</span></div>
      <div class="bar-wrap">
        <div class="bar"><i></i></div>
        <div class="bar-label">EXP {into} / {need} · 다음 레벨까지 {remain}</div>
      </div>
    </div>
    <div class="grid">
      <div class="stat"><b>{xp}</b><span>총 경험치</span></div>
      <div class="stat"><b>+{row_gain}</b><span>어젯밤 획득 전리품</span></div>
      <div class="stat"><b>{rows}</b><span>창고 스택 (데이터 행)</span></div>
      <div class="stat"><b>{stars}</b><span>명성 (stars)</span></div>
    </div>
  </section>

  <h2>인벤토리</h2>
  <div class="cards">{inventory}</div>

  <h2>현상금 게시판</h2>
  <table>
    <thead><tr><th>대상</th><th>명성</th><th>메모</th></tr></thead>
    <tbody>{quests}</tbody>
  </table>

  <h2 id="pypi">어젯밤 전리품 — PyPI</h2>
  <table>
    <thead><tr><th>드롭</th><th>시각</th></tr></thead>
    <tbody>{loot}</tbody>
  </table>

  <h2>원정 일지</h2>
  <table>
    <thead><tr><th>획득처</th><th>EXP</th></tr></thead>
    <tbody>{xp_rows}</tbody>
  </table>

  <footer>
    숫자는 가짜가 아니다. 데이터 행, 별, 사용자, 출시된 자산이 경험치가 된다.
    매일 밤 교대가 던전을 한 바퀴 돌고 창고에 쌓아 둔다.
  </footer>
</main>
</body>
</html>
"""


def _esc(value: object) -> str:
    return html.escape(str(value))


def _inventory(items: list[dict]) -> str:
    cards = []
    for item in items:
        cards.append(
            "<article class='item'>"
            f"<span class='stack'>x{ _esc(item.get('stack')) }</span>"
            f"<div class='tag { _esc(item.get('rarity')) }'>{ _esc(item.get('rarity')) } · { _esc(item.get('lane')) }</div>"
            f"<strong>{ _esc(item.get('name')) }</strong>"
            f"<p class='sub'>{ _esc(item.get('notes')) }</p>"
            "</article>"
        )
    return "".join(cards) or "<p class='sub'>빈 가방</p>"


def main() -> None:
    catalog = load_catalog()
    ledger = read_jsonl(LEDGER_PATH)
    snap = ledger[-1] if ledger else {}
    pypi = read_jsonl(ROOT / "data" / "watches" / "pypi-updates.jsonl")
    loot_items = list(reversed(pypi[-12:]))
    save = build_save(catalog, ledger, loot_items)
    write_save(save)

    candidates = []
    if SCOUT_PATH.exists():
        candidates = json.loads(SCOUT_PATH.read_text(encoding="utf-8")).get("candidates", [])
    if not candidates:
        quests = "<tr><td colspan='3'>현상금 없음. 스카우트가 다음 밤에 붙인다.</td></tr>"
    else:
        quests = "".join(
            "<tr>"
            f"<td><a href='{ _esc(c.get('url')) }'>{ _esc(c.get('name')) }</a></td>"
            f"<td>{ _esc(c.get('stars')) }</td>"
            f"<td>{ _esc(c.get('description')) }</td>"
            "</tr>"
            for c in candidates
        )

    if loot_items:
        loot = "".join(
            "<tr>"
            f"<td><a href='{ _esc(item.get('link')) }'>{ _esc(item.get('title')) }</a></td>"
            f"<td>{ _esc(item.get('published')) }</td>"
            "</tr>"
            for item in loot_items
        )
    else:
        loot = "<tr><td colspan='2'>아직 없음</td></tr>"

    labels = {
        "rows": "데이터 행",
        "nights": "원정 일수",
        "holdings": "보유 자산",
        "renown": "GitHub 명성",
        "followers": "사용자",
        "gold": "금화(MRR)",
    }
    xp_rows = "".join(
        f"<tr><td>{labels[key]}</td><td>{value}</td></tr>"
        for key, value in save["xp_parts"].items()
        if value
    )
    remain = max(save["xp_for_level"] - save["xp_into_level"], 0)
    pct = 0
    if save["xp_for_level"]:
        pct = min(100, int(100 * save["xp_into_level"] / save["xp_for_level"]))

    rows = int(snap.get("dataset_rows") or 0)
    html_out = TEMPLATE.format(
        title=_esc(save["title"]),
        guild=_esc(save["guild"]),
        hero=_esc(save["hero"]),
        nights=_esc(save["nights"]),
        generated=_esc(snap.get("date") or "n/a"),
        level=_esc(save["level"]),
        into=_esc(save["xp_into_level"]),
        need=_esc(save["xp_for_level"]),
        remain=_esc(remain),
        xp=_esc(save["xp"]),
        xp_pct=pct,
        row_gain=_esc(save["row_gain"]),
        rows=_esc(rows),
        stars=_esc(snap.get("stars") or 0),
        inventory=_inventory(save["inventory"]),
        quests=quests,
        loot=loot,
        xp_rows=xp_rows or "<tr><td colspan='2'>아직 경험치 없음</td></tr>",
    )
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD.write_text(html_out, encoding="utf-8")
    print(f"dashboard: wrote {DASHBOARD} (Lv {save['level']} {save['title']})")


if __name__ == "__main__":
    main()
