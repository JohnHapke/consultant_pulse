"""Tests for aggregator.py — pipeline orchestration."""

import pytest

from models import RAGStatus
from aggregator import (
    build_weekly_output, build_monthly_output, AggregatorError,
    _to_weekly_pulse, _build_lead_index, _avg, _avg_or_none,
)
from models import RawWeeklyEntry, RawMonthlyConsultantEntry, RawLeadEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _raw_weekly(name: str = "Anna Becker", workload: int = 3,
                blocker: bool = False, call: bool = False,
                blocker_text: str = "") -> RawWeeklyEntry:
    return RawWeeklyEntry(
        consultant_name=name, workload=workload,
        blocker_yn=blocker, blocker_text=blocker_text, call_needed=call,
    )


def _raw_monthly_c(name: str = "Anna Becker", workload: int = 3,
                   engagement: int = 4, motivation: int = 4,
                   manager_needs: str = "") -> RawMonthlyConsultantEntry:
    return RawMonthlyConsultantEntry(
        consultant_name=name, workload=workload, engagement=engagement,
        motivation=motivation, delivery=3, skill_alignment=4, task_challenge=3,
        manager_needs=manager_needs,
    )


def _raw_lead(name: str = "Anna Becker", project_status: int = 4,
              risks: str = "") -> RawLeadEntry:
    return RawLeadEntry(
        consultant_name=name, reliability=4, proactivity=4,
        skill_fit=4, project_status=project_status, risks=risks,
    )


# ---------------------------------------------------------------------------
# _avg helper
# ---------------------------------------------------------------------------

def test_avg_normal():
    assert _avg([1, 3, 5]) == 3.0


def test_avg_empty_raises():
    with pytest.raises(AggregatorError):
        _avg([])


def test_avg_rounds_to_two_decimals():
    assert _avg([1, 2]) == 1.5


def test_avg_or_none_empty_returns_none():
    assert _avg_or_none([]) is None


def test_avg_or_none_with_values():
    assert _avg_or_none([2, 4]) == 3.0


# ---------------------------------------------------------------------------
# build_weekly_output
# ---------------------------------------------------------------------------

def test_build_weekly_output_happy_path(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Anna Becker", workload=3)]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert output.week == "2026-W15"
    assert output.generated_at is not None
    assert output.aggregated.response_count == 1
    assert output.aggregated.expected_count == 17
    assert len(output.missing) == 16
    assert output.consultants[0].id == "C01"
    assert output.consultants[0].name == "Anna Becker"
    assert output.consultants[0].rag == RAGStatus.GREEN
    assert output.name_map["C01"] == "Anna Becker"


def test_build_weekly_output_blocker_flagged(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Anna Becker", blocker=True)]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert "C01" in output.blockers
    assert output.aggregated.active_blockers == 1
    assert output.aggregated.rag_red == 1


def test_build_weekly_output_call_flagged(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Anna Becker", call=True)]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert "C01" in output.calls_requested
    assert output.aggregated.calls_needed == 1
    assert output.aggregated.rag_amber == 1


def test_build_weekly_output_empty_entries_raises(consultant_map, id_name_map, rag_rules):
    with pytest.raises(AggregatorError, match="No weekly entries"):
        build_weekly_output([], consultant_map, rag_rules, "2026-W15", id_name_map)


def test_build_weekly_output_unknown_consultant_raises(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Unknown Person")]
    with pytest.raises(AggregatorError, match="Unknown consultant"):
        build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)


def test_build_weekly_output_avg_workload(consultant_map, id_name_map, rag_rules):
    entries = [
        _raw_weekly("Anna Becker", workload=2),
        _raw_weekly("Ben Müller", workload=4),
    ]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert output.aggregated.avg_workload == 3.0


def test_build_weekly_output_all_responded(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly(name) for name in consultant_map.keys()]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert output.missing == []
    assert output.aggregated.response_count == 17


# ---------------------------------------------------------------------------
# build_monthly_output
# ---------------------------------------------------------------------------

def test_build_monthly_output_happy_path(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.month == "2026-04"
    assert output.generated_at is not None
    assert output.aggregated.response_count == 1
    assert output.aggregated.lead_response_count == 1
    assert output.consultants[0].id == "C01"
    assert output.consultants[0].name == "Anna Becker"
    assert output.lead_reports[0].id == "C01"
    assert output.lead_reports[0].name == "Anna Becker"
    assert output.name_map["C01"] == "Anna Becker"


def test_build_monthly_output_empty_consultant_entries_raises(consultant_map, id_name_map, rag_rules):
    with pytest.raises(AggregatorError, match="No monthly consultant entries"):
        build_monthly_output([], [], consultant_map, rag_rules, "2026-04", id_name_map)


def test_build_monthly_output_risk_flagged(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker", risks="Deadline at risk")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert "C01" in output.risks


def test_build_monthly_output_no_lead_reports(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    output = build_monthly_output(c_entries, [], consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.lead_reports == []
    assert output.aggregated.avg_reliability is None
    assert output.aggregated.avg_proactivity is None
    assert output.aggregated.avg_skill_fit is None
    assert output.aggregated.avg_project_status is None
    assert output.aggregated.lead_response_count == 0


def test_build_monthly_output_missing_consultants(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    output = build_monthly_output(c_entries, [], consultant_map, rag_rules, "2026-04", id_name_map)
    assert len(output.missing_consultants) == 16
    assert "C01" not in output.missing_consultants


def test_build_monthly_output_missing_leads(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert len(output.missing_leads) == 16
    assert "C01" not in output.missing_leads


def test_build_monthly_output_missing_leads_no_reports(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    output = build_monthly_output(c_entries, [], consultant_map, rag_rules, "2026-04", id_name_map)
    assert len(output.missing_leads) == 17


def test_build_monthly_output_unknown_consultant_in_lead_raises(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Ghost Person")]
    with pytest.raises(AggregatorError, match="Unknown consultant"):
        build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)


def test_build_monthly_output_rag_red_low_project_status(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker", project_status=1)]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.aggregated.rag_red == 1


# ---------------------------------------------------------------------------
# Free-text pass-through (V1.1)
# ---------------------------------------------------------------------------

def test_weekly_blocker_text_passes_through(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Anna Becker", blocker=True, blocker_text="  Access to test rig blocked  ")]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert output.consultants[0].blocker_text == "Access to test rig blocked"


def test_weekly_blocker_text_empty_when_absent(consultant_map, id_name_map, rag_rules):
    entries = [_raw_weekly("Anna Becker")]
    output = build_weekly_output(entries, consultant_map, rag_rules, "2026-W15", id_name_map)
    assert output.consultants[0].blocker_text == ""


def test_monthly_manager_needs_passes_through(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker", manager_needs="  Need clarity on Q3 targets  ")]
    output = build_monthly_output(c_entries, [], consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.consultants[0].manager_needs == "Need clarity on Q3 targets"


def test_monthly_lead_risks_text_passes_through(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker", risks="  Deadline at risk due to supplier delay  ")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.lead_reports[0].risks_text == "Deadline at risk due to supplier delay"
    assert output.lead_reports[0].risks_present is True


def test_monthly_lead_risks_text_empty_when_absent(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.lead_reports[0].risks_text == ""
    assert output.lead_reports[0].risks_present is False


def test_monthly_lead_risks_text_whitespace_only(consultant_map, id_name_map, rag_rules):
    c_entries = [_raw_monthly_c("Anna Becker")]
    l_entries = [_raw_lead("Anna Becker", risks="   ")]
    output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, "2026-04", id_name_map)
    assert output.lead_reports[0].risks_text == ""
    assert output.lead_reports[0].risks_present is False
