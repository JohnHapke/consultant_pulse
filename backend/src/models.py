"""Pydantic models for consultant-pulse data pipeline."""

from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator


ConsultantId = str  # e.g. "C01" .. "C17"
Scale5 = Literal[1, 2, 3, 4, 5]


class RAGStatus(str, Enum):
    RED = "red"
    AMBER = "amber"
    GREEN = "green"


def _validate_consultant_id(v: str) -> str:
    if not (v.startswith("C") and v[1:].isdigit() and 1 <= int(v[1:]) <= 17):
        raise ValueError(f"Invalid consultant ID: {v!r} — expected C01..C17")
    return v


# ---------------------------------------------------------------------------
# Form 1 — Weekly Pulse (raw, contains personal data)
# ---------------------------------------------------------------------------

class RawWeeklyEntry(BaseModel):
    """One Form 1 submission — contains consultant name (personal data)."""

    consultant_name: str = Field(..., description="Full name from Forms — removed after ID mapping")
    workload: Scale5
    blocker_yn: bool
    blocker_text: str = Field(default="", description="Free-text — personal data stripped before output")
    call_needed: bool


class ConsultantWeeklyPulse(BaseModel):
    """Form 1 record — ID-keyed, name included for dashboard display."""

    id: ConsultantId
    name: str
    workload: Scale5
    blocker: bool
    call_needed: bool
    rag: RAGStatus = RAGStatus.GREEN

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        return _validate_consultant_id(v)


# ---------------------------------------------------------------------------
# Form 2 — Monthly Self-Assessment (raw, contains personal data)
# ---------------------------------------------------------------------------

class RawMonthlyConsultantEntry(BaseModel):
    """One Form 2 submission — contains consultant name (personal data)."""

    consultant_name: str
    workload: Scale5
    engagement: Scale5
    motivation: Scale5
    delivery: Scale5
    skill_alignment: Scale5
    task_challenge: Scale5
    manager_needs: str = Field(default="", description="Free-text — personal data stripped before output")


class ConsultantMonthlyPulse(BaseModel):
    """Form 2 record — ID-keyed, name included for dashboard display."""

    id: ConsultantId
    name: str
    workload: Scale5
    engagement: Scale5
    motivation: Scale5
    delivery: Scale5
    skill_alignment: Scale5
    task_challenge: Scale5
    rag: RAGStatus = RAGStatus.GREEN

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        return _validate_consultant_id(v)


# ---------------------------------------------------------------------------
# Form 3 — Monthly PL Report (raw, contains personal data)
# ---------------------------------------------------------------------------

class RawLeadEntry(BaseModel):
    """One Form 3 submission — contains consultant name (personal data)."""

    consultant_name: str
    reliability: Scale5
    proactivity: Scale5
    skill_fit: Scale5
    project_status: Scale5
    risks: str = Field(default="", description="Free-text — personal data stripped before output")


class LeadMonthlyReport(BaseModel):
    """Form 3 record — ID-keyed, name included for dashboard display."""

    id: ConsultantId
    name: str
    reliability: Scale5
    proactivity: Scale5
    skill_fit: Scale5
    project_status: Scale5
    risks_present: bool = False

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        return _validate_consultant_id(v)


# ---------------------------------------------------------------------------
# Aggregated output models — cockpit-first design
# ---------------------------------------------------------------------------

class WeeklyAggregated(BaseModel):
    """Team-level summary for one week."""

    avg_workload: float = Field(..., ge=1.0, le=5.0)
    active_blockers: int = Field(..., ge=0)
    calls_needed: int = Field(..., ge=0)
    rag_red: int = Field(..., ge=0)
    rag_amber: int = Field(..., ge=0)
    rag_green: int = Field(..., ge=0)
    response_count: int = Field(..., ge=0)
    expected_count: int = Field(..., ge=0)


class WeeklyPulseOutput(BaseModel):
    """Top-level output written to data/output/pulse_YYYY-WNN.json."""

    week: str = Field(..., pattern=r"^\d{4}-W\d{2}$", description="ISO week e.g. 2026-W15")
    generated_at: datetime
    aggregated: WeeklyAggregated
    name_map: dict[str, str] = Field(default_factory=dict, description="ID→name for all consultants")
    blockers: list[ConsultantId]
    calls_requested: list[ConsultantId]
    missing: list[ConsultantId]
    consultants: list[ConsultantWeeklyPulse]


class MonthlyAggregated(BaseModel):
    """Team-level summary for one month — combines Form 2 + Form 3 data."""

    avg_workload: float = Field(..., ge=1.0, le=5.0)
    avg_engagement: float = Field(..., ge=1.0, le=5.0)
    avg_motivation: float = Field(..., ge=1.0, le=5.0)
    avg_delivery: float = Field(..., ge=1.0, le=5.0)
    avg_skill_alignment: float = Field(..., ge=1.0, le=5.0)
    avg_task_challenge: float = Field(..., ge=1.0, le=5.0)
    avg_reliability: float | None = Field(default=None, ge=1.0, le=5.0)
    avg_proactivity: float | None = Field(default=None, ge=1.0, le=5.0)
    avg_skill_fit: float | None = Field(default=None, ge=1.0, le=5.0)
    avg_project_status: float | None = Field(default=None, ge=1.0, le=5.0)
    lead_response_count: int = Field(..., ge=0)
    rag_red: int = Field(..., ge=0)
    rag_amber: int = Field(..., ge=0)
    rag_green: int = Field(..., ge=0)
    response_count: int = Field(..., ge=0)
    expected_count: int = Field(..., ge=0)


class MonthlyPulseOutput(BaseModel):
    """Top-level output written to data/output/pulse_YYYY-MM.json."""

    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="e.g. 2026-04")
    generated_at: datetime
    aggregated: MonthlyAggregated
    name_map: dict[str, str] = Field(default_factory=dict, description="ID→name for all consultants")
    risks: list[ConsultantId]
    missing_consultants: list[ConsultantId]
    missing_leads: list[ConsultantId]
    consultants: list[ConsultantMonthlyPulse]
    lead_reports: list[LeadMonthlyReport]
