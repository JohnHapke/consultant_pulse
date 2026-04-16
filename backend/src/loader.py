"""Loads raw pulse data from Excel into Pydantic models.

Reads pulse_data.xlsx using the column mapping defined in config/fields.yaml.
All validation happens at this boundary — downstream code receives clean models.

The Excel accumulates all submissions over time (running table). Each load
function filters by period (week or month) and keeps the latest submission
per consultant to handle resubmissions.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from models import RawWeeklyEntry, RawMonthlyConsultantEntry, RawLeadEntry


class LoaderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_sheet(path: Path, sheet_name: str) -> pd.DataFrame:
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except FileNotFoundError:
        raise LoaderError(f"Excel file not found: {path}")
    except ValueError as e:
        raise LoaderError(f"Sheet '{sheet_name}' not found in {path.name}: {e}") from e
    except Exception as e:
        raise LoaderError(f"Cannot read '{sheet_name}' from {path.name}: {e}") from e


def _check_columns(df: pd.DataFrame, required: list[str], sheet: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise LoaderError(f"Sheet '{sheet}' missing columns: {missing}")


def _filter_by_week(df: pd.DataFrame, ts_col: str, week: str) -> pd.DataFrame:
    """Keep rows whose timestamp falls in the given ISO week (e.g. '2026-W15').

    dayfirst=True matches the DD/MM/YYYY HH:MM format written by Microsoft Forms.
    """
    year, week_num = int(week[:4]), int(week[6:])
    ts = pd.to_datetime(df[ts_col], dayfirst=True, errors="coerce")
    iso = ts.dt.isocalendar()
    mask = (iso["year"] == year) & (iso["week"] == week_num)
    return df[mask].copy()


def _filter_by_month(df: pd.DataFrame, ts_col: str, month: str) -> pd.DataFrame:
    """Keep rows whose timestamp falls in the given month (e.g. '2026-04').

    dayfirst=True matches the DD/MM/YYYY HH:MM format written by Microsoft Forms.
    """
    year, mon = int(month[:4]), int(month[5:7])
    ts = pd.to_datetime(df[ts_col], dayfirst=True, errors="coerce")
    mask = (ts.dt.year == year) & (ts.dt.month == mon)
    return df[mask].copy()


def _latest_per_consultant(df: pd.DataFrame, name_col: str, ts_col: str) -> pd.DataFrame:
    """Keep the latest submission per consultant (handles resubmissions)."""
    if df.empty:
        return df
    df = df.copy()
    df["_ts"] = pd.to_datetime(df[ts_col], dayfirst=True, errors="coerce")
    df = (
        df.sort_values("_ts", ascending=False)
        .drop_duplicates(subset=[name_col], keep="first")
        .drop(columns=["_ts"])
        .reset_index(drop=True)
    )
    return df


def _to_int(value: object, field: str) -> int:
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        raise LoaderError(f"Field '{field}': expected integer, got {value!r}") from e


def _to_bool(value: object, true_val: str, false_val: str, field: str) -> bool:
    if isinstance(value, bool):
        return value
    norm = str(value).strip()
    if norm == true_val:
        return True
    if norm == false_val:
        return False
    raise LoaderError(f"Field '{field}': expected {true_val!r} or {false_val!r}, got {value!r}")


def _optional_str(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


# ---------------------------------------------------------------------------
# Row parsers — one per form type
# ---------------------------------------------------------------------------

def _parse_weekly_row(row: pd.Series, cols: dict, bool_true: str, bool_false: str) -> RawWeeklyEntry:
    return RawWeeklyEntry(
        consultant_name=str(row[cols["consultant_name"]]).strip(),
        workload=_to_int(row[cols["workload"]], "workload"),
        blocker_yn=_to_bool(row[cols["blocker_yn"]], bool_true, bool_false, "blocker_yn"),
        blocker_text=_optional_str(row[cols["blocker_text"]]),
        call_needed=_to_bool(row[cols["call_needed"]], bool_true, bool_false, "call_needed"),
    )


def _parse_monthly_consultant_row(row: pd.Series, cols: dict) -> RawMonthlyConsultantEntry:
    return RawMonthlyConsultantEntry(
        consultant_name=str(row[cols["consultant_name"]]).strip(),
        workload=_to_int(row[cols["workload"]], "workload"),
        engagement=_to_int(row[cols["engagement"]], "engagement"),
        motivation=_to_int(row[cols["motivation"]], "motivation"),
        delivery=_to_int(row[cols["delivery"]], "delivery"),
        skill_alignment=_to_int(row[cols["skill_alignment"]], "skill_alignment"),
        task_challenge=_to_int(row[cols["task_challenge"]], "task_challenge"),
        manager_needs=_optional_str(row[cols["manager_needs"]]),
    )


def _parse_lead_row(row: pd.Series, cols: dict) -> RawLeadEntry:
    return RawLeadEntry(
        consultant_name=str(row[cols["consultant_name"]]).strip(),
        reliability=_to_int(row[cols["reliability"]], "reliability"),
        proactivity=_to_int(row[cols["proactivity"]], "proactivity"),
        skill_fit=_to_int(row[cols["skill_fit"]], "skill_fit"),
        project_status=_to_int(row[cols["project_status"]], "project_status"),
        risks=_optional_str(row[cols["risks"]]),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_weekly_pulse(path: Path, config: dict, week: str) -> list[RawWeeklyEntry]:
    """Load Form 1 data for the given ISO week (e.g. '2026-W15').

    Filters the running Excel table by submission timestamp and keeps
    the latest entry per consultant to handle resubmissions.
    """
    cfg = config["weekly_pulse"]
    cols = cfg["columns"]
    df = _read_sheet(path, cfg["sheet"])
    _check_columns(df, list(cols.values()), cfg["sheet"])
    df = _filter_by_week(df, cols["timestamp"], week)
    df = _latest_per_consultant(df, cols["consultant_name"], cols["timestamp"])
    results: list[RawWeeklyEntry] = []
    for i, row in df.iterrows():
        try:
            results.append(_parse_weekly_row(row, cols, cfg["bool_true"], cfg["bool_false"]))
        except (LoaderError, ValueError) as e:
            raise LoaderError(f"WeeklyPulse row {i}: {e}") from e
    return results


def load_monthly_consultant(path: Path, config: dict, month: str) -> list[RawMonthlyConsultantEntry]:
    """Load Form 2 data for the given month (e.g. '2026-04').

    Filters the running Excel table by submission timestamp and keeps
    the latest entry per consultant to handle resubmissions.
    """
    cfg = config["monthly_consultant"]
    cols = cfg["columns"]
    df = _read_sheet(path, cfg["sheet"])
    _check_columns(df, list(cols.values()), cfg["sheet"])
    df = _filter_by_month(df, cols["timestamp"], month)
    df = _latest_per_consultant(df, cols["consultant_name"], cols["timestamp"])
    results: list[RawMonthlyConsultantEntry] = []
    for i, row in df.iterrows():
        try:
            results.append(_parse_monthly_consultant_row(row, cols))
        except (LoaderError, ValueError) as e:
            raise LoaderError(f"MonthlyConsultant row {i}: {e}") from e
    return results


def load_monthly_lead(path: Path, config: dict, month: str) -> list[RawLeadEntry]:
    """Load Form 3 data for the given month (e.g. '2026-04').

    Filters the running Excel table by submission timestamp and keeps
    the latest PL entry per consultant to handle resubmissions.
    """
    cfg = config["monthly_lead"]
    cols = cfg["columns"]
    df = _read_sheet(path, cfg["sheet"])
    _check_columns(df, list(cols.values()), cfg["sheet"])
    df = _filter_by_month(df, cols["timestamp"], month)
    df = _latest_per_consultant(df, cols["consultant_name"], cols["timestamp"])
    results: list[RawLeadEntry] = []
    for i, row in df.iterrows():
        try:
            results.append(_parse_lead_row(row, cols))
        except (LoaderError, ValueError) as e:
            raise LoaderError(f"MonthlyLead row {i}: {e}") from e
    return results
