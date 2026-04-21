"""Generates synthetic pulse_data.xlsx and consultant_map.yaml for development.

Usage (from projects/consultant-pulse/):
  python src/generate_synthetic.py

Outputs:
  data/synthetic/pulse_data.xlsx     — Excel with all 3 sheets
  data/synthetic/consultant_map.yaml — synthetic name→ID mapping
"""

import argparse
import random
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"

CONSULTANTS: dict[str, str] = {
    "Anna Becker": "C01", "Ben Müller": "C02", "Clara Fischer": "C03",
    "David Wagner": "C04", "Eva Schulz": "C05", "Felix Bauer": "C06",
    "Greta Koch": "C07", "Hans Richter": "C08", "Iris Klein": "C09",
    "Jan Wolf": "C10", "Karin Braun": "C11", "Lars Zimmermann": "C12",
    "Maria Hartmann": "C13", "Nils Krause": "C14", "Olga Fuchs": "C15",
    "Peter Lange": "C16", "Quin Hoffmann": "C17",
}

# DD/MM/YYYY HH:MM — matches Power Automate / Microsoft Forms output format
_TS = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")


_BLOCKER_SAMPLES = [
    "Access to test rig blocked — waiting for IT ticket.",
    "Supplier has not delivered spec v2, can't continue integration.",
    "CI pipeline broken on main since Monday.",
    "Waiting for safety approval from functional safety team.",
    "Customer portal credentials expired — request pending 4 days.",
]

_MANAGER_NEEDS_SAMPLES = [
    "Need clarity on Q3 scope — feature list keeps changing.",
    "Would like a 1:1 to discuss next project rotation.",
    "Training budget for ISO 26262 refresher would help.",
    "Escalation on tooling blockers takes too long.",
    "",
]

_RISK_SAMPLES = [
    "Deadline at risk due to supplier delay on module X.",
    "Consultant overloaded on two parallel projects.",
    "Customer escalated twice last week — needs executive attention.",
    "Technical debt blocking feature delivery.",
    "",
]


def _weekly_row(name: str) -> dict:
    blocker = random.random() < 0.2
    return {
        "Timestamp": _TS, "ConsultantName": name,
        "Workload": random.randint(1, 5),
        "BlockerYN": "Yes" if blocker else "No",
        "BlockerText": random.choice(_BLOCKER_SAMPLES) if blocker else "",
        "CallNeeded": "Yes" if random.random() < 0.15 else "No",
    }


def _monthly_consultant_row(name: str) -> dict:
    return {
        "Timestamp": _TS, "ConsultantName": name,
        "Workload": random.randint(2, 5), "Engagement": random.randint(2, 5),
        "Motivation": random.randint(2, 5), "Delivery": random.randint(2, 5),
        "SkillAlignment": random.randint(1, 5), "TaskChallenge": random.randint(2, 5),
        "ManagerNeeds": random.choice(_MANAGER_NEEDS_SAMPLES),
    }


def _monthly_lead_row(name: str) -> dict:
    return {
        "Timestamp": _TS, "ConsultantName": name,
        "Reliability": random.randint(2, 5), "Proactivity": random.randint(2, 5),
        "SkillFit": random.randint(2, 5), "ProjectStatus": random.randint(2, 5),
        "Risks": random.choice(_RISK_SAMPLES),
    }


def generate_excel(output_path: Path) -> None:
    names = list(CONSULTANTS.keys())
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame([_weekly_row(n) for n in names]).to_excel(
            writer, sheet_name="WeeklyPulse", index=False
        )
        pd.DataFrame([_monthly_consultant_row(n) for n in names]).to_excel(
            writer, sheet_name="MonthlyConsultant", index=False
        )
        pd.DataFrame([_monthly_lead_row(n) for n in names]).to_excel(
            writer, sheet_name="MonthlyLead", index=False
        )


def generate_consultant_map(output_path: Path) -> None:
    entries = [{"id": cid, "name": name} for name, cid in CONSULTANTS.items()]
    data = {"consultants": entries}
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def generate(output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    excel_path = output_dir / "pulse_data.xlsx"
    map_path = output_dir / "consultant_map.yaml"
    generate_excel(excel_path)
    generate_consultant_map(map_path)
    print(f"Excel:           {excel_path}")
    print(f"Consultant map:  {map_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic pulse data")
    parser.add_argument("--date", help="ISO date for timestamps, e.g. 2026-04-07 (default: today)")
    args = parser.parse_args()
    if args.date:
        _TS = datetime.fromisoformat(args.date).strftime("%d/%m/%Y 10:00")
    generate()
