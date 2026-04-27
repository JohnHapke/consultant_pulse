# Consultant Pulse

> Weekly and monthly pulse dashboard for distributed consultant teams — anonymized, RAG-coded, trend-aware.

Built for a Delivery Manager overseeing 17 consultants across the German automotive cluster. Consultants submit short check-ins via Microsoft Forms; the Python pipeline anonymizes all data and computes RAG status; the React dashboard renders the current state with period-over-period trend comparison.

**No names ever leave the pipeline** — all output uses IDs (C01–C17).

---

## What it does

| Layer | What happens |
|-------|-------------|
| **Input** | 3 Microsoft Forms (weekly consultant, monthly consultant, monthly project lead) |
| **Transport** | Power Automate writes each submission as an Excel row to OneDrive |
| **Pipeline** | Python reads Excel, maps names → IDs, computes RAG, aggregates |
| **Output** | Anonymized JSON files — one per period |
| **Dashboard** | React SPA reads JSON, shows RAG grid, workload chart, trend deltas |

### Dashboard views

- **Weekly** — RAG status, workload (1–5), blockers, call requests, missing submissions
- **Monthly** — Consultant self-assessment scores + project lead scores, per-consultant detail rows, trend vs. previous month

All trend indicators compare the current period against the previous one automatically.

---

## Architecture

```
Microsoft Forms (3 forms)
  → Power Automate (trigger on submit → Excel row)
  → Excel / OneDrive  (sheets: WeeklyPulse, MonthlyConsultant, MonthlyLead)
  → Python aggregator (anonymize · RAG · aggregate)
  → JSON  (frontend/public/data/)
  → React dashboard
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data input | Microsoft Forms + Power Automate |
| Pipeline | Python 3.12 · pandas · pydantic v2 · pyyaml |
| Tests | pytest — 84 unit tests |
| Dashboard | React 19 · Vite · Tailwind CSS 3 |
| Fonts | Barlow Condensed · Barlow · JetBrains Mono (self-hosted) |
| Config | YAML (field mappings + RAG rules — no code changes for threshold tuning) |

---

## Project Structure

```
consultant-pulse/
├── backend/
│   ├── src/
│   │   ├── models.py              Pydantic data models
│   │   ├── loader.py              Excel → validated models (anonymization boundary)
│   │   ├── mapper.py              Name → ID mapping, missing submission detection
│   │   ├── rag.py                 RAG computation driven by rag_rules.yaml
│   │   ├── aggregator.py          Pipeline orchestration + CLI entry point
│   │   ├── writer.py              JSON serialization + index.json management
│   │   └── generate_synthetic.py  Synthetic data generator for development
│   └── tests/                     84 unit tests (pytest)
├── frontend/
│   ├── src/
│   │   ├── App.jsx                Root — view toggle, data loading
│   │   ├── hooks/usePulseData.js  Fetches JSON from public/data/
│   │   ├── utils/                 RAG colors, delta/trend helpers, data joins
│   │   └── components/            Header, SituationBlock, RAGGrid, WorkloadChart,
│   │                              MonthlyScores, ConsultantCards, …
│   └── public/data/               JSON output (one file per period + index.json)
├── config/
│   ├── fields.yaml                Excel column → Python field mapping
│   └── rag_rules.yaml             RAG thresholds (edit here, not in code)
├── data/
│   └── synthetic/                 Synthetic Excel + consultant map for demo/dev
├── requirements.txt
└── pyproject.toml
```

---

## Quick Start (synthetic data)

### Windows (WSL or Git Bash)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then generate data and start the dashboard:

```bash

# 2. Generate data for two periods (enables trend comparison)
python backend/src/aggregator.py \
  --excel data/synthetic/pulse_data.xlsx \
  --consultant-map data/synthetic/consultant_map.yaml \
  --week 2026-W15 --output frontend/public/data

python backend/src/aggregator.py \
  --excel data/synthetic/pulse_data.xlsx \
  --consultant-map data/synthetic/consultant_map.yaml \
  --week 2026-W16 --output frontend/public/data

# 3. Frontend
cd frontend
npm install
npm run dev                     # → http://localhost:5173
```

Swap `--week` for `--month 2026-03` / `--month 2026-04` to see the monthly view.

---

## Running Tests

```bash
pytest                          # from repo root with venv active
```

---

## Production Setup

### 1. Consultant map

Create `config/consultant_map.yaml` (gitignored — never committed):

```yaml
consultants:
  - id: C01
    name: Actual Name
  - id: C02
    name: Actual Name
  # … up to C17
```

### 2. Process a period

```bash
source venv/bin/activate

# Weekly:
python backend/src/aggregator.py \
  --excel /path/to/pulse_data.xlsx \
  --consultant-map config/consultant_map.yaml \
  --week 2026-W17 \
  --output frontend/public/data

# Monthly:
python backend/src/aggregator.py \
  --excel /path/to/pulse_data.xlsx \
  --consultant-map config/consultant_map.yaml \
  --month 2026-04 \
  --output frontend/public/data
```

The aggregator appends to `frontend/public/data/index.json` automatically. The dashboard always loads the two most recent periods.

### 3. Serve the dashboard

```bash
cd frontend
npm run serve       # build + python http.server → http://localhost:8080
```

Or build for static hosting (SharePoint, any CDN):

```bash
cd frontend
npm run build       # → dist/
```

---

## Adjusting RAG Rules

Edit `config/rag_rules.yaml` — no code changes needed.

| Status | Weekly trigger | Monthly trigger |
|--------|---------------|----------------|
| RED | Blocker active · workload = 5 | project_status ≤ 2 · workload = 5 · engagement/motivation ≤ 2 |
| AMBER | Workload ≥ 4 · call requested | project_status ≤ 3 · risks present · workload ≥ 4 |
| GREEN | Everything nominal | Everything nominal |

> Missing project lead report → `project_status` defaults to 3 → AMBER. Intentional: absence of signal is treated as a cautionary state.

---

## Security Notes

- `config/consultant_map.yaml` is gitignored — contains real names, share out-of-band
- JSON output contains IDs only — names are stripped in the Python pipeline before any file is written
- React auto-escapes all rendered values — no XSS risk from JSON data

---

## License

MIT
