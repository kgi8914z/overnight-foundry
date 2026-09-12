import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { catalogSchema, eventSchema } from "./schema";

const repoRoot = path.resolve(__dirname, "../../../..");

describe("catalog schema", () => {
  it("accepts the live catalog.json", () => {
    const raw = JSON.parse(readFileSync(path.join(repoRoot, "catalog.json"), "utf8"));
    const parsed = catalogSchema.parse(raw);
    expect(parsed.version).toBe(2);
    expect(parsed.assets.some((a) => a.id === "foundry")).toBe(true);
    const specimen = parsed.assets.find((a) => a.id === "watch-pypi-updates");
    expect(specimen?.specimen).toBe(true);
  });

  it("rejects a revive lane", () => {
    const raw = JSON.parse(readFileSync(path.join(repoRoot, "catalog.json"), "utf8"));
    raw.assets[0].lane = "revive";
    expect(() => catalogSchema.parse(raw)).toThrow();
  });

  it("requires a visitor id on events", () => {
    expect(() => eventSchema.parse({ type: "self_use", asset: "foundry" })).toThrow();
    expect(eventSchema.parse({ type: "self_use", asset: "foundry", vid: "abcd" }).type).toBe("self_use");
  });
});
