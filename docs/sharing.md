# Sharing the Dashboard

## Problem this solves

The dashboard runs locally with a dev server during development. For a colleague to use it,
they need a static build served over HTTP — not a Vite dev server.

This document describes how to:
1. Build the dashboard to a configurable output directory
2. Serve it locally with `npx serve`
3. Keep development data separate from real data

---

## Data separation

`frontend/public/data/` is gitignored. It holds pulse JSON files locally but is never committed.

| Location | Purpose | Tracked |
|---|---|---|
| `frontend/public/data/` | Active data for dev and build | No (gitignored) |
| `data/synthetic/output/` | Synthetic periods for dev/testing | Yes |
| `data/output/` | Real aggregator output (intermediate) | No (gitignored) |

This means `git pull` will never overwrite your local data files.

---

## Local development (with synthetic data)

```bash
# From project root
bash scripts/use-synthetic-data.sh
# or: cd frontend && npm run use-synthetic

cd frontend && npm run dev
# → http://localhost:5173
```

---

## Sharing with a colleague

### Step 1 — Build the dashboard

```bash
# From project root
bash scripts/publish.sh --output-dir ./dashboard_output
```

This builds the React app to `./dashboard_output/`.

### Step 2 — Inject data

Run the aggregator once per period, pointing output at the dashboard's data folder:

```bash
python backend/src/aggregator.py \
  --excel /path/to/data.xlsx \
  --consultant-map /path/to/consultant_map.yaml \
  --week 2026-W18 \
  --output ./dashboard_output/data
```

Repeat with `--week` or `--month` for each period you want to include.
`writer.py` updates `index.json` automatically after each run.

### Step 3 — Serve

```bash
npx serve ./dashboard_output
# → http://localhost:3000
```

The colleague opens the URL in their browser. No Node.js or Python required on their end —
they only need a browser (or you share the IP/port over the local network).

---

## Serving an already-built dist/

If you have already run `npm run build` and want to serve without rebuilding:

```bash
cd frontend && npm run serve-dist
# equivalent to: npx serve dist
```

---

## Default build (no custom output dir)

```bash
cd frontend && npm run serve
# builds to dist/ and serves via npx serve
```

---

## serve vs. publish.sh

| Command | Output dir | Rebuilds |
|---|---|---|
| `npm run serve` | `frontend/dist/` | Yes |
| `npm run serve-dist` | `frontend/dist/` | No |
| `scripts/publish.sh --output-dir <dir>` | `<dir>` | Yes |
