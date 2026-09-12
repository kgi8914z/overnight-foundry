# Overnight Foundry

밤 교대 공장의 관제소. 테마는 두 개만 허용한다.

- `revive-*` — 유용한데 죽은 오픈소스를 되살린다
- `watch-*` — 매일 행이 늘어나는 공개 데이터 + 작은 뷰어

사람은 아침 CEO다. 에이전트는 초안만 만든다.

## 아침에 할 일 (8분)

1. [briefing/LATEST.md](briefing/LATEST.md) 또는 [dashboard/index.html](dashboard/index.html)을 연다
2. 열린 PR에 `merge` / `hold` / `kill`만 답한다
3. 끝

주말에는 Build를 하지 않는다. GitHub Action `night-shift`는 매일 06:00 KST에 장부만 갱신한다.

## 레일

| 파일 | 역할 |
|---|---|
| `catalog.json` | 자산 장부. 살아 있는 테마 자산 상한 8 |
| `playbooks/` | Scout / Build / Brief / Tend / Kill |
| `AGENTS.md` | 밤 교대가 지키는 규칙 |
| `ledger/metrics.jsonl` | 숫자 시계열 |
| `data/watches/` | 복리 데이터 |
| `backlog/candidates.json` | 부활 후보 |

## 로컬에서 밤 교대 한 번

```
python scripts/validate.py
python scripts/collect_pypi_updates.py
python scripts/scout_abandoned.py
python scripts/brief.py
python scripts/render_dashboard.py
```

`gh`가 있으면 스타 수와 죽은 레포 후보를 채운다. 없어도 수집기와 장부는 돈다.

## 승인 게이트

자동: 이슈, draft PR, 데이터/브리핑/대시보드 갱신.

사람: 머지, 레포 생성·삭제, 스토어, 결제, 메일, 시크릿, archive 확정.

## 지금 있는 자산

1. 이 관제소
2. `watch-pypi-updates` — PyPI 공식 RSS. 매일 새 패키지 행이 붙는다
