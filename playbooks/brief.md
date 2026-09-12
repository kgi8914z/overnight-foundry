# Brief

Goal: one file the human can read in 60 seconds.

Run:

```
python scripts/collect_pypi_updates.py
python scripts/scout_abandoned.py
python scripts/brief.py
python scripts/render_dashboard.py
```

Write `briefing/YYYY-MM-DD.md` with only:

- What changed overnight
- Open draft PRs that need a decision
- Kill candidates
- Metric deltas (assets, dataset rows, stars, users, workflows)

Do not write essays. Do not propose a new product line.
