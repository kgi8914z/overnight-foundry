import { NextResponse } from "next/server";
import { dashboardState } from "@/lib/load";

export const dynamic = "force-dynamic";

export function GET() {
  try {
    return NextResponse.json(dashboardState());
  } catch (error) {
    const message = error instanceof Error ? error.message : "state failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
