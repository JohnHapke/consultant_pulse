"""Tests for rag.py — RAG status computation."""

import pytest
import yaml
from pathlib import Path

from models import ConsultantWeeklyPulse, ConsultantMonthlyPulse, LeadMonthlyReport, RAGStatus
from rag import load_rag_rules, compute_weekly_rag, compute_monthly_rag, RagError


# ---------------------------------------------------------------------------
# load_rag_rules
# ---------------------------------------------------------------------------

def test_load_rag_rules_success(tmp_path, rag_rules):
    path = tmp_path / "rag_rules.yaml"
    with path.open("w") as f:
        yaml.dump(rag_rules, f)
    result = load_rag_rules(path)
    assert "weekly" in result
    assert "monthly" in result


def test_load_rag_rules_not_found():
    with pytest.raises(RagError, match="not found"):
        load_rag_rules(Path("/nonexistent/rag_rules.yaml"))


def test_load_rag_rules_invalid_yaml(tmp_path):
    path = tmp_path / "rag_rules.yaml"
    path.write_text("[\ninvalid: {")
    with pytest.raises(RagError, match="Invalid YAML"):
        load_rag_rules(path)


# ---------------------------------------------------------------------------
# Weekly RAG
# ---------------------------------------------------------------------------

def _weekly_pulse(**kwargs) -> ConsultantWeeklyPulse:
    defaults = {"id": "C01", "name": "Anna Becker", "workload": 3, "blocker": False, "call_needed": False}
    return ConsultantWeeklyPulse(**(defaults | kwargs))


def test_weekly_rag_green(rag_rules):
    pulse = _weekly_pulse(workload=3, blocker=False, call_needed=False)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.GREEN


def test_weekly_rag_red_blocker(rag_rules):
    pulse = _weekly_pulse(blocker=True, workload=3)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.RED


def test_weekly_rag_red_overload(rag_rules):
    pulse = _weekly_pulse(workload=5, blocker=False)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.RED


def test_weekly_rag_red_blocker_beats_amber_workload(rag_rules):
    pulse = _weekly_pulse(blocker=True, workload=4)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.RED


def test_weekly_rag_amber_high_workload(rag_rules):
    pulse = _weekly_pulse(workload=4, blocker=False, call_needed=False)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.AMBER


def test_weekly_rag_amber_call_needed(rag_rules):
    pulse = _weekly_pulse(workload=2, blocker=False, call_needed=True)
    assert compute_weekly_rag(pulse, rag_rules) == RAGStatus.AMBER


def test_weekly_rag_empty_rules():
    pulse = _weekly_pulse(blocker=True, workload=5, call_needed=True)
    assert compute_weekly_rag(pulse, {}) == RAGStatus.GREEN


# ---------------------------------------------------------------------------
# Monthly RAG
# ---------------------------------------------------------------------------

def _monthly_pulse(**kwargs) -> ConsultantMonthlyPulse:
    # engagement=4, motivation=4 avoids the amber rule (lte 3) by default
    defaults = {
        "id": "C01", "name": "Anna Becker", "workload": 3, "engagement": 4, "motivation": 4,
        "delivery": 3, "skill_alignment": 3, "task_challenge": 3,
    }
    return ConsultantMonthlyPulse(**(defaults | kwargs))


def _lead_report(**kwargs) -> LeadMonthlyReport:
    defaults = {
        "id": "C01", "name": "Anna Becker", "reliability": 4, "proactivity": 4,
        "skill_fit": 4, "project_status": 4, "risks_present": False,
    }
    return LeadMonthlyReport(**(defaults | kwargs))


def test_monthly_rag_green(rag_rules):
    pulse = _monthly_pulse()
    lead = _lead_report()
    assert compute_monthly_rag(pulse, lead, rag_rules) == RAGStatus.GREEN


def test_monthly_rag_red_low_project_status(rag_rules):
    pulse = _monthly_pulse()
    lead = _lead_report(project_status=2)
    assert compute_monthly_rag(pulse, lead, rag_rules) == RAGStatus.RED


def test_monthly_rag_red_overload(rag_rules):
    pulse = _monthly_pulse(workload=5)
    assert compute_monthly_rag(pulse, None, rag_rules) == RAGStatus.RED


def test_monthly_rag_red_low_engagement(rag_rules):
    pulse = _monthly_pulse(engagement=2)
    assert compute_monthly_rag(pulse, None, rag_rules) == RAGStatus.RED


def test_monthly_rag_red_low_motivation(rag_rules):
    pulse = _monthly_pulse(motivation=2)
    assert compute_monthly_rag(pulse, None, rag_rules) == RAGStatus.RED


def test_monthly_rag_amber_project_status_3(rag_rules):
    pulse = _monthly_pulse()
    lead = _lead_report(project_status=3)
    assert compute_monthly_rag(pulse, lead, rag_rules) == RAGStatus.AMBER


def test_monthly_rag_amber_risks_present(rag_rules):
    pulse = _monthly_pulse()
    lead = _lead_report(project_status=4, risks_present=True)
    assert compute_monthly_rag(pulse, lead, rag_rules) == RAGStatus.AMBER


def test_monthly_rag_amber_high_workload(rag_rules):
    pulse = _monthly_pulse(workload=4)
    assert compute_monthly_rag(pulse, None, rag_rules) == RAGStatus.AMBER


def test_monthly_rag_no_lead_defaults_neutral(rag_rules):
    # Without lead data: project_status defaults to 3 → amber rule triggers.
    # But high engagement/motivation keeps it green only if project_status neutral.
    # project_status=3 hits amber rule, so expected result is AMBER.
    pulse = _monthly_pulse(workload=3, engagement=4, motivation=4)
    assert compute_monthly_rag(pulse, None, rag_rules) == RAGStatus.AMBER


def test_monthly_rag_unknown_condition_raises(rag_rules):
    bad_rules = {"weekly": {"red": [{"field": "blocker", "condition": "UNKNOWN", "value": True}]}}
    pulse = _weekly_pulse(blocker=True)
    from rag import RagError, _evaluate_condition
    with pytest.raises(RagError, match="Unknown condition"):
        _evaluate_condition(True, "UNKNOWN", True)
