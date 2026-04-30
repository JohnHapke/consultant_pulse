# Changelog

All notable changes to this project are documented here.
Format: [Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`

---

## [1.2.1] - 2026-04-30

### Fixed
- `--text-muted` raised from `#3E3E48` to `#606070` — section labels (RAG STATUS, WORKLOAD etc.) now readable on dark background (WCAG AA compliant for large/bold text)
- Data fetch paths use `import.meta.env.BASE_URL` in all three hooks — dashboard works on SharePoint subfolders without path resolution errors

### Changed
- `scripts/publish.sh` accepts `--base <path>` flag for SharePoint deployment
- `docs/sharing.md` extended with SharePoint deployment guide (Option B) including security notes

---

## [1.2.0] - 2026-04-30

### Added
- `scripts/publish.sh` — builds React app to a configurable `--output-dir`; supports any path for multi-user or network sharing
- `scripts/use-synthetic-data.sh` — copies synthetic JSON periods to `frontend/public/data/` for local development
- `npm run serve` now uses `npx serve dist` (replaces `python3 -m http.server`)
- `npm run serve-dist` — serves an existing `dist/` without rebuilding
- `npm run use-synthetic` — npm alias for the use-synthetic-data script
- `data/synthetic/output/` — synthetic JSON periods moved here (git-tracked, for dev)
- `docs/sharing.md` — colleague sharing workflow documented

### Changed
- `frontend/public/data/` is now gitignored — real data files are never overwritten by `git pull`
- Synthetic pulse JSON removed from git tracking (files stay on disk, sourced from `data/synthetic/output/`)

---

## [1.1.0] - 2026-04-15

### Added
- History view — long-term sparklines per consultant across all archived periods
- Team health bar showing RED/AMBER/GREEN proportions per period over time
- Free-text surface — blocker text, manager needs, and risk notes shown inline
- `TrendSparkline` component with hover tooltip (SVG, fixed y-range 1–5)
- `useHistory` hook loads all archived files and builds per-consultant time series

### Fixed
- Graceful degradation when only one period exists (delta UI hidden)
- Denominator computed per period so historical response-count changes don't distort proportions

---

## [1.0.0] - 2026-04-13

### Initial Release
- Python pipeline: Excel ingestion → anonymization → RAG computation → JSON output
- React dashboard with weekly and monthly views
- RAG grid (17 tiles, sorted RED→AMBER→GREEN) with pulse animation
- Workload chart (horizontal bars, RAG-colored, sorted by workload)
- Monthly scores: consultant self-assessment + project lead perspective
- Expandable consultant cards with manager needs and risk text
- Period-over-period delta comparison (RAG trend arrows + score deltas)
- 95 unit tests, all passing
- Power Automate flows 1–4 operational
