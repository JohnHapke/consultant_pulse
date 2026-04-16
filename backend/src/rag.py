"""Computes RAG status from pulse data based on YAML-driven rules.

Rules are evaluated top-to-bottom: RED first, then AMBER, then GREEN.
The first tier where any rule matches is returned.
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from models import ConsultantWeeklyPulse, ConsultantMonthlyPulse, LeadMonthlyReport, RAGStatus


class RagError(Exception):
    pass


def load_rag_rules(path: Path) -> dict:
    """Load RAG rules from YAML config file."""
    if not path.exists():
        raise RagError(f"RAG rules file not found: {path}")
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RagError(f"Invalid YAML in {path}: {e}") from e


def _evaluate_condition(value: int | bool, condition: str, threshold: int | bool) -> bool:
    """Apply a single rule condition to a value."""
    if condition == "eq":
        return value == threshold
    if condition == "gte":
        return int(value) >= int(threshold)
    if condition == "lte":
        return int(value) <= int(threshold)
    raise RagError(f"Unknown condition: {condition!r} — use eq, gte, or lte")


def _matches_any(data: dict, rules: list[dict]) -> bool:
    """Return True if any rule in the list matches the data dict."""
    for rule in rules:
        field = rule["field"]
        if field not in data:
            continue
        if _evaluate_condition(data[field], rule["condition"], rule["value"]):
            return True
    return False


def compute_weekly_rag(pulse: ConsultantWeeklyPulse, rules: dict) -> RAGStatus:
    """Compute RAG status for one consultant from weekly pulse data."""
    weekly = rules.get("weekly", {})
    data = {
        "blocker": pulse.blocker,
        "workload": pulse.workload,
        "call_needed": pulse.call_needed,
    }
    if _matches_any(data, weekly.get("red", [])):
        return RAGStatus.RED
    if _matches_any(data, weekly.get("amber", [])):
        return RAGStatus.AMBER
    return RAGStatus.GREEN


def compute_monthly_rag(
    pulse: ConsultantMonthlyPulse,
    lead: LeadMonthlyReport | None,
    rules: dict,
) -> RAGStatus:
    """Compute RAG status from monthly consultant + optional lead data.

    If lead report is missing, project_status defaults to 3 (neutral)
    and risks_present defaults to False.
    """
    monthly = rules.get("monthly", {})
    data = {
        "workload": pulse.workload,
        "engagement": pulse.engagement,
        "motivation": pulse.motivation,
        "project_status": lead.project_status if lead else 3,
        "risks_present": lead.risks_present if lead else False,
    }
    if _matches_any(data, monthly.get("red", [])):
        return RAGStatus.RED
    if _matches_any(data, monthly.get("amber", [])):
        return RAGStatus.AMBER
    return RAGStatus.GREEN
