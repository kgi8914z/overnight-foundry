import { describe, expect, it } from "vitest";
import { crossedMilestones, datasetGrowthXp, levelFromXp } from "./xp";

describe("xp math", () => {
  it("does not let a data dump beat one repeat user at default weights", () => {
    const repeat = 250;
    const dump = datasetGrowthXp(179, 8);
    expect(dump).toBeLessThan(repeat);
    expect(dump).toBeLessThan(179 * 2);
  });

  it("does not re-fire a milestone already crossed", () => {
    expect(crossedMilestones(100, 179, [100, 500])).toEqual([]);
    expect(crossedMilestones(90, 179, [100, 500])).toEqual([100]);
  });

  it("uses a rising level curve", () => {
    expect(levelFromXp(0).level).toBe(1);
    expect(levelFromXp(150).level).toBe(2);
    expect(levelFromXp(150).need).toBe(300);
  });
});
