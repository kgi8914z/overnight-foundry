import { appendFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { eventSchema } from "@/lib/schema";
import { foundryRoot } from "@/lib/root";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const parsed = eventSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });
  }
  const day = new Date().toISOString().slice(0, 10);
  const dir = path.join(foundryRoot(), "data/events");
  mkdirSync(dir, { recursive: true });
  const row = {
    at: new Date().toISOString(),
    ...parsed.data,
  };
  appendFileSync(path.join(dir, `${day}.jsonl`), `${JSON.stringify(row)}\n`, "utf8");
  return NextResponse.json({ ok: true, wrote: `data/events/${day}.jsonl` });
}
