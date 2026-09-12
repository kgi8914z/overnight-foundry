# Build

Goal: one draft PR, then stop.

1. List issues with `status:ready` and no assignee.
2. Pick the oldest ready issue whose lane is `revive` or `watch`.
3. Create branch `build/<issue-number>-<slug>`.
4. Implement only the DoD.
5. Run the relevant script or test.
6. Update `catalog.json` if a new asset was born.
7. Run `python scripts/render_dashboard.py` if data or catalog changed.
8. Open a **draft** PR that links the issue.
9. Comment what the morning CEO should do: merge / hold / kill.

If you cannot finish in one session, push WIP and say what is left. Do not start a second issue.
