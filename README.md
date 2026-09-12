# Overnight Foundry

밤 교대 선택 공장. 많이 만들지 않고, 많이 실험한 뒤 사용량으로 죽인다.

사람은 아침 CEO. Cursor는 출고 교대. Claude/Codex는 생각과 어려운 한 방.

- `utility-*` — 반복되는 작은 문제의 MVP
- `watch-*` — 매일 커지는 공개 데이터 → viewer → API → utility
- 첫 자산은 이 공장의 대시보드 자신

스펙: [docs/v2-spec.md](docs/v2-spec.md)

## 아침에 할 일

1. [dashboard/index.html](dashboard/index.html) 또는 [briefing/LATEST.md](briefing/LATEST.md)
2. MERGE / HOLD / KILL
3. 끝

## 슬롯

Incubator 4 · Growing 2 · Maintenance 2 · Archived 무제한.

새 실험을 열려면 하나를 승격하거나 죽여야 한다.

## 길드 홀 (로컬)

```
cd apps/web
npm install
npm test
npm run dev
```

http://localhost:3000 — 배포는 사람 승인 후에만.

## 밤 교대

```
python scripts/night_shift.py
```

매일 06:00 KST GitHub Action이 장부를 갱신한다. 머지와 배포는 하지 않는다.
