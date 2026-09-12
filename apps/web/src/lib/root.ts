import path from "node:path";

export function foundryRoot(): string {
  if (process.env.FOUNDRY_ROOT) return process.env.FOUNDRY_ROOT;
  return path.resolve(process.cwd(), "../..");
}
