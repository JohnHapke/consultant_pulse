"""Shared pytest fixtures for consultant-pulse tests."""

import pytest
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# Consultant map — 17 synthetic entries
# ---------------------------------------------------------------------------

@pytest.fixture
def consultant_map() -> dict[str, str]:
    """Flat alias→ID lookup as returned by load_consultant_map."""
    return {
        "Anna Becker": "C01", "Ben Müller": "C02", "Clara Fischer": "C03",
        "David Wagner": "C04", "Eva Schulz": "C05", "Felix Bauer": "C06",
        "Greta Koch": "C07", "Hans Richter": "C08", "Iris Klein": "C09",
        "Jan Wolf": "C10", "Karin Braun": "C11", "Lars Zimmermann": "C12",
        "Maria Hartmann": "C13", "Nils Krause": "C14", "Olga Fuchs": "C15",
        "Peter Lange": "C16", "Quin Hoffmann": "C17",
    }


@pytest.fixture
def id_name_map() -> dict[str, str]:
    """ID→canonical name lookup as returned by load_id_name_map."""
    return {
        "C01": "Anna Becker", "C02": "Ben Müller", "C03": "Clara Fischer",
        "C04": "David Wagner", "C05": "Eva Schulz", "C06": "Felix Bauer",
        "C07": "Greta Koch", "C08": "Hans Richter", "C09": "Iris Klein",
        "C10": "Jan Wolf", "C11": "Karin Braun", "C12": "Lars Zimmermann",
        "C13": "Maria Hartmann", "C14": "Nils Krause", "C15": "Olga Fuchs",
        "C16": "Peter Lange", "C17": "Quin Hoffmann",
    }


@pytest.fixture
def consultant_map_yaml() -> dict:
    """Structured YAML input format for load_consultant_map tests."""
    return {
        "consultants": [
            {"id": "C01", "name": "Anna Becker",      "email": "anna.becker@example.com",      "aliases": ["Becker, Anna"]},
            {"id": "C02", "name": "Ben Müller",        "email": "ben.mueller@example.com",       "aliases": ["Müller, Ben"]},
            {"id": "C03", "name": "Clara Fischer",     "email": "clara.fischer@example.com",     "aliases": ["Fischer, Clara"]},
            {"id": "C04", "name": "David Wagner",      "email": "david.wagner@example.com",      "aliases": ["Wagner, David"]},
            {"id": "C05", "name": "Eva Schulz",        "email": "eva.schulz@example.com",        "aliases": ["Schulz, Eva"]},
            {"id": "C06", "name": "Felix Bauer",       "email": "felix.bauer@example.com",       "aliases": ["Bauer, Felix"]},
            {"id": "C07", "name": "Greta Koch",        "email": "greta.koch@example.com",        "aliases": ["Koch, Greta"]},
            {"id": "C08", "name": "Hans Richter",      "email": "hans.richter@example.com",      "aliases": ["Richter, Hans"]},
            {"id": "C09", "name": "Iris Klein",        "email": "iris.klein@example.com",        "aliases": ["Klein, Iris"]},
            {"id": "C10", "name": "Jan Wolf",          "email": "jan.wolf@example.com",          "aliases": ["Wolf, Jan"]},
            {"id": "C11", "name": "Karin Braun",       "email": "karin.braun@example.com",       "aliases": ["Braun, Karin"]},
            {"id": "C12", "name": "Lars Zimmermann",   "email": "lars.zimmermann@example.com",   "aliases": ["Zimmermann, Lars"]},
            {"id": "C13", "name": "Maria Hartmann",    "email": "maria.hartmann@example.com",    "aliases": ["Hartmann, Maria"]},
            {"id": "C14", "name": "Nils Krause",       "email": "nils.krause@example.com",       "aliases": ["Krause, Nils"]},
            {"id": "C15", "name": "Olga Fuchs",        "email": "olga.fuchs@example.com",        "aliases": ["Fuchs, Olga"]},
            {"id": "C16", "name": "Peter Lange",       "email": "peter.lange@example.com",       "aliases": ["Lange, Peter"]},
            {"id": "C17", "name": "Quin Hoffmann",     "email": "quin.hoffmann@example.com",     "aliases": ["Hoffmann, Quin"]},
        ]
    }


# ---------------------------------------------------------------------------
# RAG rules — mirrors config/rag_rules.yaml
# ---------------------------------------------------------------------------

@pytest.fixture
def rag_rules() -> dict:
    return {
        "weekly": {
            "red": [
                {"field": "blocker", "condition": "eq", "value": True},
                {"field": "workload", "condition": "gte", "value": 5},
            ],
            "amber": [
                {"field": "workload", "condition": "gte", "value": 4},
                {"field": "call_needed", "condition": "eq", "value": True},
            ],
        },
        "monthly": {
            "red": [
                {"field": "project_status", "condition": "lte", "value": 2},
                {"field": "workload", "condition": "gte", "value": 5},
                {"field": "engagement", "condition": "lte", "value": 2},
                {"field": "motivation", "condition": "lte", "value": 2},
            ],
            "amber": [
                {"field": "project_status", "condition": "lte", "value": 3},
                {"field": "risks_present", "condition": "eq", "value": True},
                {"field": "workload", "condition": "gte", "value": 4},
                {"field": "engagement", "condition": "lte", "value": 3},
                {"field": "motivation", "condition": "lte", "value": 3},
            ],
        },
    }


# ---------------------------------------------------------------------------
# Minimal Excel file with all 3 sheets
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_excel(tmp_path: Path) -> Path:
    """Single-row Excel with timestamps in 2026-W15 (= 2026-04-07, Tuesday)."""
    path = tmp_path / "pulse_data.xlsx"
    # "07/04/2026 09:00" = Tuesday of 2026-W15, in month 2026-04
    # Uses the same DD/MM/YYYY HH:MM format written by Microsoft Forms / Power Automate
    weekly = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": [3], "BlockerYN": ["No"], "BlockerText": [""], "CallNeeded": ["No"],
    }
    monthly_c = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Workload": [3], "Engagement": [4], "Motivation": [4], "Delivery": [3],
        "SkillAlignment": [4], "TaskChallenge": [3], "ManagerNeeds": [""],
    }
    monthly_l = {
        "Timestamp": ["07/04/2026 09:00"], "ConsultantName": ["Anna Becker"],
        "Reliability": [4], "Proactivity": [3], "SkillFit": [4],
        "ProjectStatus": [4], "Risks": [""],
    }
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(weekly).to_excel(writer, sheet_name="WeeklyPulse", index=False)
        pd.DataFrame(monthly_c).to_excel(writer, sheet_name="MonthlyConsultant", index=False)
        pd.DataFrame(monthly_l).to_excel(writer, sheet_name="MonthlyLead", index=False)
    return path


# ---------------------------------------------------------------------------
# Fields config — mirrors config/fields.yaml
# ---------------------------------------------------------------------------

@pytest.fixture
def fields_config() -> dict:
    return {
        "weekly_pulse": {
            "sheet": "WeeklyPulse",
            "bool_true": "Yes",
            "bool_false": "No",
            "columns": {
                "timestamp": "Timestamp", "consultant_name": "ConsultantName",
                "workload": "Workload", "blocker_yn": "BlockerYN",
                "blocker_text": "BlockerText", "call_needed": "CallNeeded",
            },
        },
        "monthly_consultant": {
            "sheet": "MonthlyConsultant",
            "columns": {
                "timestamp": "Timestamp", "consultant_name": "ConsultantName",
                "workload": "Workload", "engagement": "Engagement",
                "motivation": "Motivation", "delivery": "Delivery",
                "skill_alignment": "SkillAlignment", "task_challenge": "TaskChallenge",
                "manager_needs": "ManagerNeeds",
            },
        },
        "monthly_lead": {
            "sheet": "MonthlyLead",
            "columns": {
                "timestamp": "Timestamp", "consultant_name": "ConsultantName",
                "reliability": "Reliability", "proactivity": "Proactivity",
                "skill_fit": "SkillFit", "project_status": "ProjectStatus",
                "risks": "Risks",
            },
        },
    }
