import { z } from "zod";

export const metricsSchema = z.object({
  unique_users: z.number().int().nonnegative(),
  repeat_users: z.number().int().nonnegative(),
  active_users_1d: z.number().int().nonnegative(),
  api_calls: z.number().int().nonnegative(),
  dataset_records: z.number().int().nonnegative(),
  paying_users: z.number().int().nonnegative(),
  self_uses_weekly: z.number().int().nonnegative(),
  backlinks: z.number().int().nonnegative(),
  stars: z.number().int().nonnegative(),
});

export const assetSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  lane: z.enum(["utility", "watch", "ext", "service", "ops"]),
  lifecycle: z.enum(["idea", "incubator", "shipped", "growing", "maintenance", "archived"]),
  repo: z.string().min(1),
  problem: z.string().min(1),
  user: z.string().min(1),
  mvp: z.string().min(1),
  kill: z.string().min(1),
  specimen: z.boolean().optional(),
  role: z.string().optional(),
  data_path: z.string().optional(),
  source: z.string().optional(),
  license: z.string().optional(),
  born: z.string().optional(),
  shipped_at: z.string().nullable().optional(),
  last_measured_at: z.string().optional(),
  metrics: metricsSchema,
});

export const catalogSchema = z.object({
  version: z.literal(2),
  owner: z.string(),
  org: z.string().nullable(),
  control_plane: z.string(),
  campaign_start: z.string(),
  measured_on: z.string().optional(),
  assets: z.array(assetSchema).min(1),
});

export const eventSchema = z.object({
  type: z.enum(["page_view", "self_use", "api_call", "decision"]),
  asset: z.string().min(1).default("foundry"),
  vid: z.string().min(4).max(80),
  decision: z.enum(["MERGE", "HOLD", "KILL"]).optional(),
});

export const xpAwardSchema = z.object({
  at: z.string(),
  date: z.string().optional(),
  asset: z.string(),
  reason: z.string(),
  delta: z.number(),
  xp: z.number().int(),
  milestones: z.array(z.number()).optional(),
});

export const approvalItemSchema = z.object({
  kind: z.enum(["merge", "deploy", "archive", "hold"]),
  ref: z.string(),
  title: z.string(),
  url: z.string().nullable().optional(),
  draft: z.boolean().optional(),
});

export type Catalog = z.infer<typeof catalogSchema>;
export type Asset = z.infer<typeof assetSchema>;
export type FactoryEvent = z.infer<typeof eventSchema>;
export type XpAward = z.infer<typeof xpAwardSchema>;
export type ApprovalItem = z.infer<typeof approvalItemSchema>;
