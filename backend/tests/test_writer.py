"""Tests for writer.py — JSON serialization."""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from models import (
    WeeklyPulseOutput, WeeklyAggregated, ConsultantWeeklyPulse,
    MonthlyPulseOutput, MonthlyAggregated, ConsultantMonthlyPulse, LeadMonthlyReport,
    RAGStatus,
)
from writer import write_weekly, write_monthly, WriterError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def weekly_output() -> WeeklyPulseOutput:
    return WeeklyPulseOutput(
        week="2026-W15",
        generated_at=datetime(2026, 4, 15, 8, 0, 0, tzinfo=timezone.utc),
        aggregated=WeeklyAggregated(
            avg_workload=3.0, active_blockers=0, calls_needed=0,
            rag_red=0, rag_amber=0, rag_green=1,
            response_count=1, expected_count=17,
        ),
        name_map={"C01": "Anna Becker", "C02": "Ben Müller"},
        blockers=[], calls_requested=[], missing=["C02"],
        consultants=[ConsultantWeeklyPulse(
            id="C01", name="Anna Becker", workload=3, blocker=False, call_needed=False, rag=RAGStatus.GREEN
        )],
    )


@pytest.fixture
def monthly_output() -> MonthlyPulseOutput:
    return MonthlyPulseOutput(
        month="2026-04",
        generated_at=datetime(2026, 4, 15, 8, 0, 0, tzinfo=timezone.utc),
        aggregated=MonthlyAggregated(
            avg_workload=3.0, avg_engagement=4.0, avg_motivation=4.0,
            avg_delivery=3.0, avg_skill_alignment=4.0, avg_task_challenge=3.0,
            avg_reliability=4.0, avg_proactivity=3.0, avg_skill_fit=4.0,
            avg_project_status=4.0, lead_response_count=1,
            rag_red=0, rag_amber=0, rag_green=1,
            response_count=1, expected_count=17,
        ),
        name_map={"C01": "Anna Becker"},
        risks=[], missing_consultants=[], missing_leads=[],
        consultants=[ConsultantMonthlyPulse(
            id="C01", name="Anna Becker", workload=3, engagement=4, motivation=4,
            delivery=3, skill_alignment=4, task_challenge=3, rag=RAGStatus.GREEN,
        )],
        lead_reports=[LeadMonthlyReport(
            id="C01", name="Anna Becker", reliability=4, proactivity=3, skill_fit=4,
            project_status=4, risks_present=False,
        )],
    )


# ---------------------------------------------------------------------------
# write_weekly
# ---------------------------------------------------------------------------

def test_write_weekly_creates_file(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    assert path.exists()


def test_write_weekly_correct_filename(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    assert path.name == "pulse_2026-W15.json"


def test_write_weekly_valid_json(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert data["week"] == "2026-W15"
    assert data["aggregated"]["avg_workload"] == 3.0
    assert data["consultants"][0]["id"] == "C01"


def test_write_weekly_creates_output_dir(tmp_path, weekly_output):
    nested = tmp_path / "deep" / "nested" / "output"
    write_weekly(weekly_output, nested)
    assert nested.exists()


def test_write_weekly_cockpit_fields_present(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert "blockers" in data
    assert "calls_requested" in data
    assert "missing" in data
    assert "generated_at" in data
    agg = data["aggregated"]
    assert "rag_red" in agg
    assert "rag_amber" in agg
    assert "rag_green" in agg
    assert "response_count" in agg
    assert "expected_count" in agg


def test_write_weekly_name_map_serialized(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert "name_map" in data
    assert data["name_map"]["C01"] == "Anna Becker"
    assert data["consultants"][0]["name"] == "Anna Becker"


# ---------------------------------------------------------------------------
# write_monthly
# ---------------------------------------------------------------------------

def test_write_monthly_creates_file(tmp_path, monthly_output):
    path = write_monthly(monthly_output, tmp_path)
    assert path.exists()


def test_write_monthly_correct_filename(tmp_path, monthly_output):
    path = write_monthly(monthly_output, tmp_path)
    assert path.name == "pulse_2026-04.json"


def test_write_monthly_valid_json(tmp_path, monthly_output):
    path = write_monthly(monthly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert data["month"] == "2026-04"
    assert data["aggregated"]["avg_engagement"] == 4.0
    assert len(data["lead_reports"]) == 1


def test_write_monthly_cockpit_fields_present(tmp_path, monthly_output):
    path = write_monthly(monthly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert "risks" in data
    assert "missing_consultants" in data
    assert "missing_leads" in data
    assert "generated_at" in data
    agg = data["aggregated"]
    assert "lead_response_count" in agg


def test_write_monthly_name_map_serialized(tmp_path, monthly_output):
    path = write_monthly(monthly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert "name_map" in data
    assert data["name_map"]["C01"] == "Anna Becker"
    assert data["consultants"][0]["name"] == "Anna Becker"
    assert data["lead_reports"][0]["name"] == "Anna Becker"


def test_write_weekly_overwrites_existing(tmp_path, weekly_output):
    path = write_weekly(weekly_output, tmp_path)
    path.write_text("old content")
    write_weekly(weekly_output, tmp_path)
    with path.open() as f:
        data = json.load(f)
    assert data["week"] == "2026-W15"
