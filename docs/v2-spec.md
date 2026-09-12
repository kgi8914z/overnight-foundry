# Overnight Foundry v2

선택과 도태의 공장. Cursor는 밤 교대 출고, Claude/Codex는 생각과 어려운 한 방.
첫 자산은 공장 자신(`apps/web` 대시보드)이다. Canvas는 보조다.

## 목표

많이 만들지 않는다. 많이 실험하고, 사용량으로 죽이고, 남은 것만 키운다.

90일 성공:

- shipped experiments: 12
- archived: ~8
- surviving (Growing + Maintenance): ~4
- repeat user가 있는 asset: 2+
- 매일 늘어나는 dataset: 1+
- 길드장이 매주 직접 쓰는 asset: 1+
- 아침 brief + dashboard만으로 운영

실패: 살아 있는 레포 12개를 자랑스러워하는 것.

## 루프

```
Scout → Spec → Build → Test → Draft PR
  → Human merge → Deploy → Measure → Improve | Kill
```

Build만 반복하면 공장 사망이다. Deploy와 Measure가 없는 이슈는 `status:blocked`.

## 레인

| prefix | 하는 일 | 확장 |
|---|---|---|
| `utility-*` | 반복되는 작은 문제를 푸는 웹/CLI/데스크톱 | 사용량 있으면 Improve |
| `watch-*` | 매일 커지는 공개 데이터 | viewer → API → utility |
| `ext-*` | 브라우저 확장. utility의 배포 형태 | 스토어는 사람 |
| `service-*` | 승격된 utility의 상주 서비스 | Growing만 |
| `ops-*` | 공장 자신. 슬롯 밖 | 항상 1개 |

`revive-*` 금지. 죽은 오픈소스 부활은 기본 테마가 아니다.

## 슬롯

| 버킷 | 최대 | 누가 들어가나 |
|---|---|---|
| Incubator | 4 | `idea` 제외, `incubator` + `shipped` |
| Growing | 2 | 반복 사용이 증명된 것 |
| Maintenance | 2 | 안정화된 winner |
| Archived | 무제한 | 죽은 실험 |

`ops`는 슬롯을 먹지 않는다. 새 Incubator를 열려면 기존 1개를 archive하거나 Growing으로 승격해야 한다.

월별 밤 교대 비중:

| 월 | Build(신규/MVP) | Improve(winner) |
|---|---|---|
| 1 | 70 | 30 |
| 2 | 50 | 50 |
| 3+ | 30 | 70 |

## 수명

```
idea → incubator → shipped → growing → maintenance
                 ↘ archived     ↘ archived
```

| 전이 | 조건 | 승인 |
|---|---|---|
| idea → incubator | spec+DoD+킬조건, Incubator 빈 자리 | 사람 코멘트 `incubate` |
| incubator → shipped | merge + deploy + beacon 부착 | 사람 merge/deploy |
| shipped → growing | 7일 내 repeat_users≥3 또는 self_uses_weekly≥3, Growing 빈 자리 | 사람 `promote` |
| shipped → archived | 14일 repeat_users=0 이고 self_uses_weekly=0 | 사람 `kill` |
| incubator → archived | 21일 shipped 못 함, 또는 사람 kill | 사람 `kill` |
| growing → maintenance | 14일 연속 사용 유지, 큰 기능 없음, Maintenance 빈 자리 | 사람 `maintain` |
| growing → archived | 사용 붕괴 14일 | 사람 `kill` |
| * → archived | 법적/ToS/사고 | 사람만 |

에이전트는 라벨만 단다. 최종 폐기는 사람.

## GitHub

지금은 org 없이 `kgi8914z/overnight-foundry` 한 레포가 control-plane이다.

org `overnight-foundry`를 나중에 만들면:

```
overnight-foundry/
  foundry          # 이 레포를 이전. 유일한 워크스페이스
  utility-<slug>
  watch-<slug>
  ext-<slug>
  service-<slug>
```

자산 레포는 **최초 public release** 때 사람이 만든다. Incubator는 control-plane의 `incubator/<id>/`에서 시작한다. 묘지 레포를 미리 만들지 않는다.

## Control-plane 트리 (목표)

```
overnight-foundry/
  AGENTS.md
  foundry.config.json
  catalog.json
  catalog.schema.json
  apps/web/                 # Next.js. 첫 utility이자 길드 홀
  packages/schema/
  packages/xp/
  packages/metrics/
  data/watches/
  data/events/              # beacon 원장
  ledger/metrics.jsonl
  briefing/LATEST.md
  backlog/candidates.json
  playbooks/
  scripts/scout.py
  scripts/brief.py
  scripts/measure.py
  scripts/tend.py
  scripts/kill_review.py
  scripts/night_shift.py
  incubator/                # 아직 독립 레포가 아닌 MVP
  .github/ISSUE_TEMPLATE/
  .github/workflows/
```

정적 `dashboard/index.html`은 v1 잔재다. v2 대시보드가 뜨면 그 파일이 이 앱을 가리키는 진입점만 남긴다.

## catalog.json

`version: 2`. 자산 필수 필드:

```
id, name, lane, lifecycle, repo, problem, user, mvp, kill
metrics.unique_users
metrics.repeat_users
metrics.active_users_1d
metrics.api_calls
metrics.dataset_records
metrics.paying_users
metrics.self_uses_weekly
metrics.backlinks
metrics.stars
born, shipped_at, last_measured_at
```

`lane`: utility | watch | ext | service | ops  
`lifecycle`: idea | incubator | shipped | growing | maintenance | archived

슬롯 계산에서 `ops`와 `idea`와 `archived`는 제외. `shipped`는 Incubator 자리를 계속 먹는다.

## 이슈 템플릿 / DoD

라벨: `lane:utility|watch|ext`, `work:build|improve|measure|spec`, `status:ready|blocked`, `phase:scout|spec|build|review`.

Body 필수:

- 누가 일주일 몇 번 겪는 문제인가
- MVP 한 문장
- 측정 방법 (beacon 이벤트 이름)
- 배포 방법
- 14/21일 kill 조건
- 하지 않을 것

Build 금지: DoD 없음, measure 계획 없음, Incubator 만석, 이번 달 Improve 비중 미달인데 신규만 집어 감.

PR DoD:

- 테스트 또는 collector dry-run
- beacon 또는 dataset append
- catalog 갱신
- brief/dashboard가 새 자산이나 메트릭을 읽음
- 시크릿 없음
- 초안 PR, 머지하지 않음

## 자동화

| 이름 | 언제 | 하는 일 | 멈추는 곳 |
|---|---|---|---|
| Scout | 매일 02:00 KST | 후보 ≤5, 이슈만 | 구현 안 함. 만석이면 중지 |
| Spec | Scout 직후 | ready 이슈에 측정/배포/킬 초안 | 사람 `incubate` 전 코딩 금지 |
| Build | 03:00 | 월 mix에 따라 build 또는 improve 1건 | draft PR |
| Test | Build 안 | 단위 + 브라우저 QA 체크리스트 | 실패면 PR에 blocked |
| Brief | 06:00 | 장부, XP, LATEST.md, 대시보드 데이터 | 머지/배포 안 함 |
| Measure | Brief 전 | events → catalog.metrics | 추정 금지. 없으면 0 |
| Tend | 수 03:00 | Growing/Maintenance만 버그/수집기 | 새 기능 금지 |
| Kill review | 1일 03:00 | 조건 맞는 자산에 kill-candidate | archive는 사람 |

GitHub Action이 장부 루프를 먼저 돈다. Cursor Cloud Agent는 Build/Spec/브라우저 QA가 필요할 때 켠다.

## 승인

자동: 조사, 이슈, spec 초안, 브랜치, 구현, 테스트, 브라우저 QA, 문서, draft PR, 데이터 refresh, brief, Growing 자산의 작은 버그.

사람: 최초 public release, production 큰 변경, 결제, 외부 메일/DM, 시크릿, 스토어, 애매한 수집, 최종 폐기, 레포 생성.

아침 답은 세 개: MERGE / HOLD / KILL.

## 대시보드 데이터

`apps/web`이 읽는 모델 (파일 또는 `/api/state`):

```
report.date
report.completed[]     {asset, fact}
report.waiting[]       {kind: merge|deploy|archive, ref, title}
report.metrics         {active, users_1d, repeat, records, mrr, xp, level}
report.empire          {title, xp_into, xp_need}
catalog.assets[]
backlog.candidates[]
ledger.recent[]
events.daily[]
```

Canvas 금지. 배포는 Cloudflare Pages 또는 GitHub Pages(정적 export). Cursor를 꺼도 `apps/web` + `catalog.json` + Action이 남는다.

## XP

허영 낮게, 사용 높게.

| 신호 | 점 |
|---|---|
| unique_users | 40 |
| repeat_users | 120 |
| active_users_1d | 80 |
| api_calls | 1 |
| dataset_records | 2 |
| paying_users | 800 |
| self_uses_weekly | 60 |
| backlinks | 90 |
| stars | 5 |
| 원정 1일 | 20 |

레벨: 필요치 `150 * level`. 칭호는 사용 기반이지 유물 사냥이 아니다.

stars만 올려서 레벨 업 금지에 가깝게 둔다.

## 측정

1. `apps/web`의 `POST /api/event` (나중에). 지금은 `data/events/YYYY-MM-DD.jsonl`.
2. 모든 shipped UI는 `foundry_id` + `event` + anonymous `vid` 를 보낸다. IP/이름 저장 금지.
3. watch는 collector가 `dataset_records`를 센다.
4. 길드장 자기 사용은 대시보드의 “오늘 씀” 또는 `scripts/self_use.py`.
5. Measure가 catalog.metrics를 덮어쓴다. 추측 숫자 금지.
6. GitHub stars는 참고 필드일 뿐 XP 가중 최저.

## 1주차

1. 레일 v2 고정 (catalog, AGENTS, playbooks, 이슈 템플릿). revive 제거.
2. `foundry.config.json` + validate가 슬롯을 거부.
3. `apps/web` 골격: 아침 리포트 / 대기열 / XP / 자산 수명.
4. catalog + briefing + ledger를 앱이 읽게.
5. `data/events` + self-use + Measure 스크립트.
6. 정적 HTML 대시보드를 앱 링크로 교체. watch-pypi는 앱의 한 패널.
7. 배포(사람). beacon을 공장에 부착. 이게 첫 shipped.

## 30일

- 매일 06:00 Action: collect / measure / brief
- 평일 아침 8분: MERGE/HOLD/KILL
- 주 1 Improve (공장 자신 또는 사용 있는 watch)
- 주 1 이하 신규. 만석이면 신규 0
- 14일: shipped 없이 멈춘 incubator kill-review
- 21일: 첫 utility MVP 후보 1 (공장이 측정되기 전엔 시작하지 않음)
- 30일: 공장 self_uses_weekly≥3 이면 Growing. 아니면 신규 금지하고 공장만 고친다

watch-pypi는 Incubator 1자리를 먹는다. viewer가 공장 안으로 들어오면 유지. 독립 레포는 사용이 생긴 뒤.
