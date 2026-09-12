# Scout

Goal: file at most 5 tight issues. Do not build.

## revive

Search for repositories that look useful and dead:

- archived or last push older than 24 months
- stars >= 200
- license is permissive (MIT, BSD, Apache-2.0)
- not a framework, not an awesome-list, not a course dump

Write an issue with title `revive: <name>` and labels `lane:revive`, `status:ready`.

## watch

Prefer public feeds with a license or terms that allow reuse:

- official RSS / JSON APIs
- government open data
- package registries
- standards indexes (RFC, CVE)

Do not scrape logged-in pages. Do not store personal data.

## Stop conditions

- live non-ops assets already at `live_cap`
- candidate lacks a DoD
- duplicate of an open issue or catalog id
