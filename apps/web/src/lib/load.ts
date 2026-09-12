import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { catalogSchema, type ApprovalItem, type Catalog, type XpAward } from "./schema";
import { foundryRoot } from "./root";
import { levelFromXp, titleForLevel } from "./xp";

function read(rel: string): string {
  return readFileSync(path.join(foundryRoot(), rel), "utf8");
}

function readJsonl(rel: string): Record<string, unknown>[] {
  const full = path.join(foundryRoot(), rel);
  if (!existsSync(full)) return [];
  return readFileSync(full, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line) as Record<string, unknown>);
}

export function loadCatalog(): Catalog {
  return catalogSchema.parse(JSON.parse(read("catalog.json")));
}

export function loadBriefing(): string {
  const full = path.join(foundryRoot(), "briefing/LATEST.md");
  if (!existsSync(full)) return "아직 브리핑 없음";
  return readFileSync(full, "utf8");
}

export function loadLedger(): Record<string, unknown>[] {
  return readJsonl("ledger/metrics.jsonl");
}

export function loadXpAwards(): XpAward[] {
  return readJsonl("ledger/xp.jsonl") as XpAward[];
}

export function loadApprovals(): ApprovalItem[] {
  const full = path.join(foundryRoot(), "backlog/approvals.json");
  if (!existsSync(full)) return [];
  const parsed = JSON.parse(readFileSync(full, "utf8")) as { waiting?: ApprovalItem[] };
  return parsed.waiting ?? [];
}

export function loadPypi(limit = 20): { title: string; link: string; published: string }[] {
  const catalog = loadCatalog();
  const watch = catalog.assets.find((a) => a.id === "watch-pypi-updates");
  const rel = watch?.data_path ?? "data/watches/pypi-updates.jsonl";
  const rows = readJsonl(rel) as { title?: string; link?: string; published?: string }[];
  return rows
    .slice(-limit)
    .reverse()
    .map((row) => ({
      title: String(row.title ?? ""),
      link: String(row.link ?? ""),
      published: String(row.published ?? ""),
    }));
}

export function loadEventCount(): number {
  const dir = path.join(foundryRoot(), "data/events");
  if (!existsSync(dir)) return 0;
  return readdirSync(dir)
    .filter((name) => name.endsWith(".jsonl"))
    .reduce((sum, name) => sum + readJsonl(`data/events/${name}`).length, 0);
}

export function loopStatus(input: {
  catalog: Catalog;
  briefing: string;
  ledger: unknown[];
  events: number;
  approvalsFile: boolean;
}): { green: boolean; checks: { id: string; ok: boolean; label: string }[] } {
  const checks = [
    { id: "catalog", ok: input.catalog.assets.length > 0, label: "catalog.json 유효" },
    { id: "brief", ok: input.briefing.includes("OVERNIGHT REPORT") || input.briefing.includes("Decide"), label: "Brief 생성" },
    { id: "measure", ok: Boolean(input.catalog.measured_on) && input.ledger.length > 0, label: "Measure 성공" },
    { id: "events", ok: input.events > 0, label: "event 기록" },
    { id: "queue", ok: input.approvalsFile, label: "승인 큐 파일" },
  ];
  return { green: checks.every((c) => c.ok), checks };
}

export function dashboardState() {
  const catalog = loadCatalog();
  const briefing = loadBriefing();
  const ledger = loadLedger();
  const awards = loadXpAwards();
  const waiting = loadApprovals();
  const pypi = loadPypi();
  const events = loadEventCount();
  const approvalsFile = existsSync(path.join(foundryRoot(), "backlog/approvals.json"));
  const loop = loopStatus({ catalog, briefing, ledger, events, approvalsFile });
  const totalXp = awards.reduce((sum, row) => sum + Number(row.xp || 0), 0);
  const progress = levelFromXp(totalXp);
  const last = ledger.at(-1) ?? {};
  return {
    generatedAt: new Date().toISOString(),
    catalog,
    briefing,
    waiting,
    pypi,
    loop,
    empire: {
      xp: totalXp,
      level: progress.level,
      into: progress.into,
      need: progress.need,
      title: titleForLevel(progress.level),
      lastAwards: awards.slice(-8).reverse(),
    },
    snapshot: last,
    etag: createHash("sha1").update(JSON.stringify({ catalog, totalXp, events })).digest("hex").slice(0, 12),
  };
}

export type DashboardState = ReturnType<typeof dashboardState>;
