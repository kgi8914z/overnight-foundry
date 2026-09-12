export const USER_DELTA_ORDER = [
  "repeat_users",
  "paying_users",
  "unique_users",
  "active_users_1d",
  "self_uses_weekly",
  "backlinks",
  "stars",
] as const;

export type UserDeltaKey = (typeof USER_DELTA_ORDER)[number];

export function datasetGrowthXp(newRecords: number, log2Weight: number): number {
  if (newRecords <= 0) return 0;
  return Math.floor(log2Weight * Math.log2(1 + newRecords));
}

export function apiCallsXp(newCalls: number, log2Weight: number): number {
  if (newCalls <= 0) return 0;
  return Math.floor(log2Weight * Math.log2(1 + newCalls));
}

export function crossedMilestones(prev: number, curr: number, marks: number[]): number[] {
  return marks.filter((mark) => prev < mark && mark <= curr);
}

export function levelFromXp(xp: number, step = 150): { level: number; into: number; need: number } {
  let level = 1;
  let spent = 0;
  for (;;) {
    const need = step * level;
    if (xp < spent + need) return { level, into: xp - spent, need };
    spent += need;
    level += 1;
  }
}

export function titleForLevel(level: number): string {
  const titles: [number, string][] = [
    [1, "견습 길드장"],
    [3, "밤길 실험가"],
    [5, "측정하는 서기"],
    [7, "도태의 반장"],
    [9, "선택하는 주조공"],
    [12, "제국 회계관"],
    [16, "사용량의 대마법사"],
  ];
  let title = titles[0][1];
  for (const [need, label] of titles) {
    if (level >= need) title = label;
  }
  return title;
}
