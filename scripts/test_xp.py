from __future__ import annotations

import math
import unittest

from xp import api_calls_xp, awards_for_asset, crossed_milestones, dataset_growth_xp, level_from_xp


class XpMathTest(unittest.TestCase):
    def test_dataset_log_not_linear(self) -> None:
        small = dataset_growth_xp(10, 8)
        huge = dataset_growth_xp(10_000, 8)
        self.assertGreater(small, 0)
        self.assertLess(huge, 8 * 20)
        self.assertLess(huge, 10_000 * 2)
        self.assertEqual(huge, int(8 * math.log2(1 + 10_000)))

    def test_repeat_outranks_dataset_dump(self) -> None:
        config = {
            "xp": {
                "delta": {
                    "repeat_users": 250,
                    "paying_users": 200,
                    "unique_users": 80,
                    "active_users_1d": 60,
                    "self_uses_weekly": 40,
                    "backlinks": 30,
                    "stars": 3,
                },
                "api_calls_log2": 12,
                "dataset": {"log2_weight": 8, "milestones": [100, 500], "milestone_xp": 25},
            }
        }
        user = awards_for_asset(
            "a",
            {"repeat_users": 0, "dataset_records": 0},
            {"repeat_users": 1, "dataset_records": 0},
            config,
            [],
        )
        data = awards_for_asset(
            "a",
            {"repeat_users": 0, "dataset_records": 100},
            {"repeat_users": 0, "dataset_records": 279},
            config,
            [100],
        )
        self.assertEqual(user[0]["xp"], 250)
        self.assertLess(sum(row["xp"] for row in data), 250)

    def test_no_award_on_zero_delta(self) -> None:
        config = {"xp": {"delta": {"stars": 3}, "dataset": {"log2_weight": 8, "milestones": []}}}
        rows = awards_for_asset("a", {"stars": 2, "dataset_records": 50}, {"stars": 2, "dataset_records": 50}, config, [])
        self.assertEqual(rows, [])

    def test_milestone_once(self) -> None:
        self.assertEqual(crossed_milestones(90, 120, [100, 500]), [100])
        self.assertEqual(crossed_milestones(100, 120, [100, 500]), [])

    def test_level_step(self) -> None:
        level, into, need = level_from_xp(0)
        self.assertEqual((level, into, need), (1, 0, 150))
        level, _, need = level_from_xp(150)
        self.assertEqual(level, 2)
        self.assertEqual(need, 300)

    def test_api_log(self) -> None:
        self.assertEqual(api_calls_xp(0, 12), 0)
        self.assertEqual(api_calls_xp(7, 12), int(12 * math.log2(8)))


if __name__ == "__main__":
    unittest.main()
