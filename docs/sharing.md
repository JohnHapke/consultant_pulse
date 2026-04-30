# Sharing the Dashboard

## Problem this solves

The dashboard runs locally with a dev server during development. For a colleague to use it,
they need a static build served over HTTP — not a Vite dev server.

This document describes how to:
1. Build the dashboard to a configurable output directory
2. Serve it locally with `npx serve` or deploy it to SharePoint
3. Keep development data separate from real data

---

## Data separation

`frontend/public/data/` is gitignored. It holds pulse JSON files locally but is never committed.

| Location | Purpose | Tracked |
|---|---|---|
| `frontend/public/data/` | Active data for dev and build | No (gitignored) |
| `data/synthetic/output/` | Synthetic periods for dev/testing | Yes |
| `data/output/` | Real aggregator output (intermediate) | No (gitignored) |

`git pull` will never overwrite your local data files.

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

## Option A — Local sharing via npx serve

### Step 1 — Build the dashboard

```bash
# From project root
bash scripts/publish.sh --output-dir ./dashboard_output
```

### Step 2 — Inject data

```bash
python backend/src/aggregator.py \
  --excel /path/to/data.xlsx \
  --consultant-map /path/to/consultant_map.yaml \
  --week 2026-W18 \
  --output ./dashboard_output/data
```

Repeat for each period. `writer.py` updates `index.json` automatically.

### Step 3 — Serve

```bash
npx serve ./dashboard_output
# → http://localhost:3000
```

> **Note:** `npx serve` listens on all network interfaces (0.0.0.0).
> Only use on trusted networks. Add `--listen localhost` to restrict to local-only access.

---

## Option B — SharePoint (recommended for company use)

SharePoint serves static files within the M365 tenant. Access is controlled by Entra ID —
no external exposure, no open ports, no self-managed server.

### Security
- Data stays within the company M365 tenant
- Access via M365 permissions (invite specific colleagues, not "everyone in tenant")
- Microsoft manages HTTPS, audit logs, and encryption
- Even with anonymized IDs, restrict access to people who operationally need the data (DSGVO)

### Step 1 — Find the SharePoint subfolder path

Upload the dashboard to a document library subfolder, e.g.:
`https://company.sharepoint.com/sites/TeamName/Shared Documents/dashboard/`

The `--base` path is the server-relative path to that folder:
`/sites/TeamName/Shared%20Documents/dashboard/`

### Step 2 — Build with the correct base path

```bash
bash scripts/publish.sh \
  --output-dir ./dashboard_output \
  --base "/sites/TeamName/Shared%20Documents/dashboard/"
```

### Step 3 — Inject data

```bash
python backend/src/aggregator.py \
  --excel /path/to/data.xlsx \
  --consultant-map /path/to/consultant_map.yaml \
  --week 2026-W18 \
  --output ./dashboard_output/data
```

### Step 4 — Upload to SharePoint

Copy all files from `./dashboard_output/` into the SharePoint folder
(`index.html`, `assets/`, `data/`, `favicon.svg`, `icons.svg`).

Colleagues open the SharePoint URL directly in their browser — no local setup required.

---

## Serving an existing dist/ without rebuilding

```bash
cd frontend && npm run serve-dist
# equivalent to: npx serve dist --listen localhost
```

---

## Default build (local dist/)

```bash
cd frontend && npm run serve
# builds to dist/ + serves via npx serve (localhost only)
```

---

## Command reference

| Command | Output dir | Base path | Rebuilds |
|---|---|---|---|
| `npm run serve` | `frontend/dist/` | `/` | Yes |
| `npm run serve-dist` | `frontend/dist/` | `/` | No |
| `scripts/publish.sh --output-dir <dir>` | `<dir>` | `/` | Yes |
| `scripts/publish.sh --output-dir <dir> --base <path>` | `<dir>` | `<path>` | Yes |
