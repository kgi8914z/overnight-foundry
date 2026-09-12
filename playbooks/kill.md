# Kill

An asset becomes `kill-candidate` when all are true:

- not `ops`
- `users == 0` and `stars == 0`
- older than `kill_after_days_without_users`

Morning CEO archives. Night shift only labels and lists.

After archive:

- `status` in `catalog.json` becomes `archived`
- data may stay, code freezes
- it no longer counts toward `live_cap`
