"""Tests for loader.py — Excel ingestion, period filtering, and validation."""

import pytest
import pandas as pd
from pathlib import Path

from loader import (
    load_weekly_pulse, load_monthly_consultant, load_monthly_lead, LoaderError,
)

WEEK = "2026-W15"   # 2026-04-06 Mon – 2026-04-12 Sun
MONTH = "2026-04"

# ---------------------------------------------------------------------------
# Weekly pulse — happy path + filtering
# ---------------------------------------------------------------------------

def test_load_weekly_pulse_happy_path(sample_excel, fields_config):
    entries = load_weekly_pulse(sample_excel, fields_config, WEEK)
    assert len(entries) == 1
    assert entries[0].consultant_name == "Anna Becker"
    assert entries[0].workload == 3
    assert entries[0].blocker_yn is False
    assert entries[0].call_needed is False


def test_load_weekly_pulse_wrong_week_returns_empty(sample_excel, fields_config):
    # sample_excel has timestamps in W15; filtering for W16 yields nothing
    entries = load_weekly_pulse(sample_excel, fields_config, "2026-W16")
    assert entries == []


def test_load_weekly_pulse_latest_wins_on_duplicate(tmp_path, fields_config):
    """When a consultant submits twice in the same week, keep the latest."""
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 08:00", "08/04/2026 17:00"],
        "ConsultantName": ["Anna Becker", "Anna Becker"],
        "Workload": [2, 4],
        "BlockerYN": ["No", "No"],
        "BlockerText": ["", ""],
        "CallNeeded": ["No", "No"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="WeeklyPulse", index=False)
    entries = load_weekly_pulse(path, fields_config, WEEK)
    assert len(entries) == 1
    assert entries[0].workload == 4  # later submission wins


def test_load_weekly_pulse_blocker_and_call(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Ben Müller"],
        "Workload": [5], "BlockerYN": ["Yes"], "BlockerText": ["CI broken"],
        "CallNeeded": ["Yes"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="WeeklyPulse", index=False)
    entries = load_weekly_pulse(path, fields_config, WEEK)
    assert entries[0].blocker_yn is True
    assert entries[0].call_needed is True
    assert entries[0].blocker_text == "CI broken"


def test_load_weekly_pulse_file_not_found(fields_config):
    with pytest.raises(LoaderError, match="not found"):
        load_weekly_pulse(Path("/nonexistent/file.xlsx"), fields_config, WEEK)


def test_load_weekly_pulse_sheet_not_found(tmp_path, fields_config):
    path = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(path, sheet_name="WrongSheet", index=False)
    with pytest.raises(LoaderError, match="WeeklyPulse"):
        load_weekly_pulse(path, fields_config, WEEK)


def test_load_weekly_pulse_missing_column(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    pd.DataFrame({"Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"]}).to_excel(
        path, sheet_name="WeeklyPulse", index=False
    )
    with pytest.raises(LoaderError, match="missing columns"):
        load_weekly_pulse(path, fields_config, WEEK)


def test_load_weekly_pulse_invalid_workload(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": ["not_a_number"], "BlockerYN": ["No"],
        "BlockerText": [""], "CallNeeded": ["No"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="WeeklyPulse", index=False)
    with pytest.raises(LoaderError, match="workload"):
        load_weekly_pulse(path, fields_config, WEEK)


def test_load_weekly_pulse_invalid_bool(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": [3], "BlockerYN": ["Maybe"],
        "BlockerText": [""], "CallNeeded": ["No"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="WeeklyPulse", index=False)
    with pytest.raises(LoaderError, match="blocker_yn"):
        load_weekly_pulse(path, fields_config, WEEK)


def test_load_weekly_pulse_empty_sheet(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    columns = ["Timestamp", "ConsultantName", "Workload", "BlockerYN", "BlockerText", "CallNeeded"]
    pd.DataFrame(columns=columns).to_excel(path, sheet_name="WeeklyPulse", index=False)
    entries = load_weekly_pulse(path, fields_config, WEEK)
    assert entries == []


def test_load_weekly_pulse_optional_blocker_text_none(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": [2], "BlockerYN": ["No"],
        "BlockerText": [None], "CallNeeded": ["No"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="WeeklyPulse", index=False)
    entries = load_weekly_pulse(path, fields_config, WEEK)
    assert entries[0].blocker_text == ""


# ---------------------------------------------------------------------------
# Monthly consultant
# ---------------------------------------------------------------------------

def test_load_monthly_consultant_happy_path(sample_excel, fields_config):
    entries = load_monthly_consultant(sample_excel, fields_config, MONTH)
    assert len(entries) == 1
    assert entries[0].consultant_name == "Anna Becker"
    assert entries[0].engagement == 4
    assert entries[0].motivation == 4
    assert entries[0].manager_needs == ""


def test_load_monthly_consultant_wrong_month_returns_empty(sample_excel, fields_config):
    entries = load_monthly_consultant(sample_excel, fields_config, "2026-03")
    assert entries == []


def test_load_monthly_consultant_invalid_scale(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": [3], "Engagement": ["high"], "Motivation": [4],
        "Delivery": [3], "SkillAlignment": [4], "TaskChallenge": [3],
        "ManagerNeeds": [""],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="MonthlyConsultant", index=False)
    with pytest.raises(LoaderError, match="engagement"):
        load_monthly_consultant(path, fields_config, MONTH)


# ---------------------------------------------------------------------------
# Monthly lead
# ---------------------------------------------------------------------------

def test_load_monthly_lead_happy_path(sample_excel, fields_config):
    entries = load_monthly_lead(sample_excel, fields_config, MONTH)
    assert len(entries) == 1
    assert entries[0].consultant_name == "Anna Becker"
    assert entries[0].project_status == 4
    assert entries[0].risks == ""


def test_load_monthly_lead_wrong_month_returns_empty(sample_excel, fields_config):
    entries = load_monthly_lead(sample_excel, fields_config, "2026-03")
    assert entries == []


def test_load_monthly_lead_with_risks(tmp_path, fields_config):
    path = tmp_path / "pulse.xlsx"
    data = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Reliability": [4], "Proactivity": [3], "SkillFit": [4],
        "ProjectStatus": [2], "Risks": ["Deadline at risk"],
    }
    pd.DataFrame(data).to_excel(path, sheet_name="MonthlyLead", index=False)
    entries = load_monthly_lead(path, fields_config, MONTH)
    assert entries[0].risks == "Deadline at risk"
    assert entries[0].project_status == 2
