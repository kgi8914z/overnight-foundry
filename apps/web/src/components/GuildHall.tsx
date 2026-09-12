"use client";

import { useEffect, useMemo, useState } from "react";
import type { DashboardState } from "@/lib/load";

function visitorId(): string {
  const key = "foundry_vid";
  const existing = window.localStorage.getItem(key);
  if (existing) return existing;
  const vid = crypto.randomUUID();
  window.localStorage.setItem(key, vid);
  return vid;
}

async function postEvent(payload: Record<string, unknown>) {
  await fetch("/api/event", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ vid: visitorId(), ...payload }),
  });
}

export function GuildHall({ initial }: { initial: DashboardState }) {
  const [state, setState] = useState(initial);
  const [note, setNote] = useState("");
  const pct = useMemo(() => {
    if (!state.empire.need) return 0;
    return Math.min(100, Math.round((100 * state.empire.into) / state.empire.need));
  }, [state.empire]);

  useEffect(() => {
    const key = "foundry_page_view";
    if (!sessionStorage.getItem(key)) {
      sessionStorage.setItem(key, "1");
      void postEvent({ type: "page_view", asset: "foundry" });
    }
  }, []);

  async function refresh() {
    const res = await fetch("/api/state", { cache: "no-store" });
    if (res.ok) setState((await res.json()) as DashboardState);
  }

  async function selfUse() {
    await postEvent({ type: "self_use", asset: "foundry" });
    setNote("오늘 씀 — 다음 Measure가 self_uses_weekly에 반영한다.");
  }

  async function decide(decision: "MERGE" | "HOLD" | "KILL") {
    await postEvent({ type: "decision", asset: "foundry", decision });
    setNote(`${decision} 기록됨. 사람만 실제 merge/archive를 한다.`);
  }

  const records = state.catalog.assets.reduce((sum, a) => sum + a.metrics.dataset_records, 0);
  const repeats = state.catalog.assets.reduce((sum, a) => sum + a.metrics.repeat_users, 0);
  const uniques = state.catalog.assets.reduce((sum, a) => sum + a.metrics.unique_users, 0);

  return (
    <main>
      <div className="kicker">Overnight Report</div>
      <h1>{state.empire.title}</h1>
      <p className="sub">
        {state.catalog.control_plane} · Lv {state.empire.level} · 루프 {state.loop.green ? "GREEN" : "NOT YET"} · {state.generatedAt.slice(0, 16)}
      </p>

      <section className="hero">
        <div className="row">
          <div className="lvl">
            Lv {state.empire.level}
            <span>{state.empire.title}</span>
          </div>
          <div style={{ flex: 1, minWidth: 220 }}>
            <div className="bar">
              <i style={{ width: `${pct}%` }} />
            </div>
            <p className="sub">
              EXP {state.empire.into} / {state.empire.need} · 총 {state.empire.xp} · 델타 원장만 합산
            </p>
          </div>
        </div>
        <div className="grid">
          <div className="stat">
            <b>{uniques}</b>
            <span>unique users</span>
          </div>
          <div className="stat">
            <b>{repeats}</b>
            <span>repeat users</span>
          </div>
          <div className="stat">
            <b>{records}</b>
            <span>dataset records (표본)</span>
          </div>
          <div className="stat">
            <b>{state.empire.lastAwards[0]?.xp ?? 0}</b>
            <span>마지막 XP 지급</span>
          </div>
        </div>
        <div className="actions">
          <button className="merge" onClick={() => void decide("MERGE")}>
            MERGE
          </button>
          <button onClick={() => void decide("HOLD")}>HOLD</button>
          <button className="kill" onClick={() => void decide("KILL")}>
            KILL
          </button>
          <button onClick={() => void selfUse()}>오늘 씀</button>
          <button onClick={() => void refresh()}>새로고침</button>
        </div>
        {note ? <p className="sub">{note}</p> : null}
      </section>

      <h2>루프 증명</h2>
      <table>
        <tbody>
          {state.loop.checks.map((check) => (
            <tr key={check.id}>
              <td className={check.ok ? "ok" : "no"}>{check.ok ? "OK" : "NO"}</td>
              <td>{check.label}</td>
            </tr>
          ))}
          <tr>
            <td className="ok">OK</td>
            <td>MERGE / HOLD / KILL UI</td>
          </tr>
        </tbody>
      </table>

      <h2>Waiting for approval</h2>
      <div className="queue">
        {state.waiting.length === 0 ? (
          <p className="sub">대기 없음. 표본 watch-pypi는 가치 없으면 kill 후보다.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Kind</th>
                <th>Ref</th>
                <th>Title</th>
              </tr>
            </thead>
            <tbody>
              {state.waiting.map((item) => (
                <tr key={`${item.kind}-${item.ref}`}>
                  <td>{item.kind}</td>
                  <td>
                    {item.url ? <a href={item.url}>{item.ref}</a> : item.ref}
                  </td>
                  <td>{item.title}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <h2>Assets</h2>
      <div className="cards">
        {state.catalog.assets.map((asset) => (
          <article className="item" key={asset.id}>
            <div className={`tag ${asset.specimen ? "표본" : asset.lifecycle}`}>{asset.specimen ? "표본" : asset.lifecycle} · {asset.lane}</div>
            <strong>{asset.name}</strong>
            <p className="sub">{asset.problem}</p>
            <p className="sub">
              users {asset.metrics.unique_users}/{asset.metrics.repeat_users} · records {asset.metrics.dataset_records} · self {asset.metrics.self_uses_weekly}
            </p>
            <p className="sub">kill: {asset.kill}</p>
          </article>
        ))}
      </div>

      <h2>XP awards (no double count)</h2>
      <table>
        <thead>
          <tr>
            <th>Reason</th>
            <th>Asset</th>
            <th>Δ</th>
            <th>XP</th>
          </tr>
        </thead>
        <tbody>
          {state.empire.lastAwards.length === 0 ? (
            <tr>
              <td colSpan={4}>아직 델타 없음. 첫 Measure는 cursor만 심는다.</td>
            </tr>
          ) : (
            state.empire.lastAwards.map((row, i) => (
              <tr key={`${row.at}-${row.reason}-${i}`}>
                <td>{row.reason}</td>
                <td>{row.asset}</td>
                <td>{row.delta}</td>
                <td>{row.xp}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      <h2 id="pypi">watch-pypi specimen</h2>
      <p className="sub">파이프라인 검증용. 행이 는다고 성공이 아니다. viewer/사용자 없으면 kill.</p>
      <table>
        <thead>
          <tr>
            <th>Drop</th>
            <th>When</th>
          </tr>
        </thead>
        <tbody>
          {state.pypi.map((row) => (
            <tr key={row.link + row.title}>
              <td>
                <a href={row.link}>{row.title}</a>
              </td>
              <td>{row.published}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Brief</h2>
      <pre className="brief">{state.briefing}</pre>
    </main>
  );
}
