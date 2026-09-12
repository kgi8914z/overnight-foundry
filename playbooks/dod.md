# Definition of Done

An issue is ready for Build only if it has all of these in the body:

- Lane: `revive` or `watch`
- Why this is in theme (one sentence)
- Source URL
- Done means: concrete checks, not “make it nice”
- Kill: how we will know to archive it
- Out of scope: at least one thing we will not do

A PR is ready for morning review only if:

- Tests or a collector dry-run passed
- `catalog.json` updated when a new asset appears
- README is two short sentences + run instructions
- No `.env`, keys, cookies, or scraped personal data
- Dashboard regenerated when metrics/data changed
