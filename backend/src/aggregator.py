"""Aggregation pipeline: anonymize → compute RAG → aggregate → output models.

CLI usage (run from agents/consultant-pulse/):
  python src/aggregator.py --excel data/synthetic/pulse_data.xlsx \\
    --consultant-map data/synthetic/consultant_map.yaml \\
    --rag-rules config/rag_rules.yaml \\
    --fields config/fields.yaml \\
    --output data/output/ \\
    --week 2026-W15        # or --month 2026-04
"""

import argparse
import statistics
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import (
    ConsultantWeeklyPulse, ConsultantMonthlyPulse, LeadMonthlyReport,
    WeeklyAggregated, WeeklyPulseOutput, MonthlyAggregated, MonthlyPulseOutput,
    RawWeeklyEntry, RawMonthlyConsultantEntry, RawLeadEntry, RAGStatus,
)
from loader import load_weekly_pulse, load_monthly_consultant, load_monthly_lead
from mapper import load_consultant_map, load_id_name_map, map_name_to_id, find_missing_ids, get_all_ids, MapperError
from rag import load_rag_rules, compute_weekly_rag, compute_monthly_rag
from writer import write_weekly, write_monthly


class AggregatorError(Exception):
    pass


# ---------------------------------------------------------------------------
# Weekly helpers
# ---------------------------------------------------------------------------

def _to_weekly_pulse(
    entry: RawWeeklyEntry, consultant_map: dict, rag_rules: dict, id_name_map: dict
) -> ConsultantWeeklyPulse:
    try:
        cid = map_name_to_id(entry.consultant_name, consultant_map)
    except MapperError as e:
        raise AggregatorError(str(e)) from e
    pulse = ConsultantWeeklyPulse(
        id=cid, name=id_name_map[cid],
        workload=entry.workload, blocker=entry.blocker_yn, call_needed=entry.call_needed,
    )
    pulse.rag = compute_weekly_rag(pulse, rag_rules)
    return pulse


def _build_weekly_aggregated(pulses: list[ConsultantWeeklyPulse], expected: int) -> WeeklyAggregated:
    rag_counts = {s: sum(1 for p in pulses if p.rag == s) for s in RAGStatus}
    return WeeklyAggregated(
        avg_workload=round(statistics.mean(p.workload for p in pulses), 2),
        active_blockers=sum(1 for p in pulses if p.blocker),
        calls_needed=sum(1 for p in pulses if p.call_needed),
        rag_red=rag_counts[RAGStatus.RED],
        rag_amber=rag_counts[RAGStatus.AMBER],
        rag_green=rag_counts[RAGStatus.GREEN],
        response_count=len(pulses),
        expected_count=expected,
    )


def build_weekly_output(
    entries: list[RawWeeklyEntry],
    consultant_map: dict,
    rag_rules: dict,
    week: str,
    id_name_map: dict,
) -> WeeklyPulseOutput:
    """Map names to IDs, compute RAG, and aggregate weekly entries."""
    if not entries:
        raise AggregatorError("No weekly entries to aggregate")
    pulses = [_to_weekly_pulse(e, consultant_map, rag_rules, id_name_map) for e in entries]
    aggregated = _build_weekly_aggregated(pulses, len(get_all_ids(consultant_map)))
    missing = find_missing_ids([e.consultant_name for e in entries], consultant_map)
    return WeeklyPulseOutput(
        week=week,
        generated_at=datetime.now(timezone.utc),
        aggregated=aggregated,
        name_map=id_name_map,
        blockers=[p.id for p in pulses if p.blocker],
        calls_requested=[p.id for p in pulses if p.call_needed],
        missing=missing,
        consultants=pulses,
    )


# ---------------------------------------------------------------------------
# Monthly helpers
# ---------------------------------------------------------------------------

def _build_lead_index(
    lead_entries: list[RawLeadEntry], consultant_map: dict, id_name_map: dict
) -> dict[str, LeadMonthlyReport]:
    index: dict[str, LeadMonthlyReport] = {}
    for entry in lead_entries:
        try:
            cid = map_name_to_id(entry.consultant_name, consultant_map)
        except MapperError as e:
            raise AggregatorError(str(e)) from e
        index[cid] = LeadMonthlyReport(
            id=cid,
            name=id_name_map[cid],
            reliability=entry.reliability,
            proactivity=entry.proactivity,
            skill_fit=entry.skill_fit,
            project_status=entry.project_status,
            risks_present=bool(entry.risks.strip()),
        )
    return index


def _to_monthly_pulse(
    entry: RawMonthlyConsultantEntry,
    consultant_map: dict,
    lead_index: dict,
    rag_rules: dict,
    id_name_map: dict,
) -> ConsultantMonthlyPulse:
    try:
        cid = map_name_to_id(entry.consultant_name, consultant_map)
    except MapperError as e:
        raise AggregatorError(str(e)) from e
    pulse = ConsultantMonthlyPulse(
        id=cid, name=id_name_map[cid], workload=entry.workload, engagement=entry.engagement,
        motivation=entry.motivation, delivery=entry.delivery,
        skill_alignment=entry.skill_alignment, task_challenge=entry.task_challenge,
    )
    pulse.rag = compute_monthly_rag(pulse, lead_index.get(cid), rag_rules)
    return pulse


def _avg(values: list[int]) -> float:
    if not values:
        raise AggregatorError("Cannot compute average of empty list")
    return round(statistics.mean(values), 2)


def _avg_or_none(values: list[int]) -> float | None:
    return round(statistics.mean(values), 2) if values else None


def _build_monthly_aggregated(
    pulses: list[ConsultantMonthlyPulse],
    leads: list[LeadMonthlyReport],
    expected: int,
) -> MonthlyAggregated:
    rag_counts = {s: sum(1 for p in pulses if p.rag == s) for s in RAGStatus}
    return MonthlyAggregated(
        avg_workload=_avg([p.workload for p in pulses]),
        avg_engagement=_avg([p.engagement for p in pulses]),
        avg_motivation=_avg([p.motivation for p in pulses]),
        avg_delivery=_avg([p.delivery for p in pulses]),
        avg_skill_alignment=_avg([p.skill_alignment for p in pulses]),
        avg_task_challenge=_avg([p.task_challenge for p in pulses]),
        avg_reliability=_avg_or_none([l.reliability for l in leads]),
        avg_proactivity=_avg_or_none([l.proactivity for l in leads]),
        avg_skill_fit=_avg_or_none([l.skill_fit for l in leads]),
        avg_project_status=_avg_or_none([l.project_status for l in leads]),
        lead_response_count=len(leads),
        rag_red=rag_counts[RAGStatus.RED],
        rag_amber=rag_counts[RAGStatus.AMBER],
        rag_green=rag_counts[RAGStatus.GREEN],
        response_count=len(pulses),
        expected_count=expected,
    )


def build_monthly_output(
    consultant_entries: list[RawMonthlyConsultantEntry],
    lead_entries: list[RawLeadEntry],
    consultant_map: dict,
    rag_rules: dict,
    month: str,
    id_name_map: dict,
) -> MonthlyPulseOutput:
    """Map names to IDs, compute RAG, and aggregate monthly entries."""
    if not consultant_entries:
        raise AggregatorError("No monthly consultant entries to aggregate")
    lead_index = _build_lead_index(lead_entries, consultant_map, id_name_map)
    pulses = [_to_monthly_pulse(e, consultant_map, lead_index, rag_rules, id_name_map) for e in consultant_entries]
    leads = list(lead_index.values())
    aggregated = _build_monthly_aggregated(pulses, leads, len(get_all_ids(consultant_map)))
    missing_consultants = find_missing_ids([e.consultant_name for e in consultant_entries], consultant_map)
    missing_leads = find_missing_ids([e.consultant_name for e in lead_entries], consultant_map)
    return MonthlyPulseOutput(
        month=month,
        generated_at=datetime.now(timezone.utc),
        aggregated=aggregated,
        name_map=id_name_map,
        risks=[r.id for r in leads if r.risks_present],
        missing_consultants=missing_consultants,
        missing_leads=missing_leads,
        consultants=pulses,
        lead_reports=leads,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Consultant Pulse Aggregator")
    p.add_argument("--excel", required=True, type=Path)
    p.add_argument("--consultant-map", required=True, type=Path)
    p.add_argument("--rag-rules", default=Path("config/rag_rules.yaml"), type=Path)
    p.add_argument("--fields", default=Path("config/fields.yaml"), type=Path)
    p.add_argument("--output", required=True, type=Path)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--week", help="ISO week, e.g. 2026-W15")
    group.add_argument("--month", help="Month, e.g. 2026-04")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    with args.fields.open() as f:
        fields_config = yaml.safe_load(f)
    consultant_map = load_consultant_map(args.consultant_map)
    id_name_map = load_id_name_map(args.consultant_map)
    rag_rules = load_rag_rules(args.rag_rules)

    if args.week:
        entries = load_weekly_pulse(args.excel, fields_config, args.week)
        output = build_weekly_output(entries, consultant_map, rag_rules, args.week, id_name_map)
        path = write_weekly(output, args.output)
    else:
        c_entries = load_monthly_consultant(args.excel, fields_config, args.month)
        l_entries = load_monthly_lead(args.excel, fields_config, args.month)
        output = build_monthly_output(c_entries, l_entries, consultant_map, rag_rules, args.month, id_name_map)
        path = write_monthly(output, args.output)

    print(f"Output written to: {path}")


if __name__ == "__main__":
    main()
