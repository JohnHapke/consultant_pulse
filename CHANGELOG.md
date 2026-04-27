# Changelog

All notable changes to this project are documented here.
Format: [Semantic Versioning](https://semver.org/) — `MAJOR.MINOR.PATCH`

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
