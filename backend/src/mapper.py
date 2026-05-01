"""Maps consultant names and emails to anonymized IDs.

The consultant_map.yaml contains PII (real names, emails) and is gitignored.
For development, use data/synthetic/consultant_map.yaml instead.

Format:
  consultants:
    - id: C01
      name: "Full Name"
      email: "name@company.com"
      aliases:
        - "Lastname, Firstname"   # M365 display name variants

All of name, email, and aliases are registered as lookup keys for the same ID.
"""

from pathlib import Path

import yaml


class MapperError(Exception):
    pass


def _build_lookup(entries: list[dict]) -> dict[str, str]:
    """Build flat alias→id lookup from structured consultant entries."""
    lookup: dict[str, str] = {}
    for entry in entries:
        cid = str(entry.get("id", "")).strip()
        if not cid:
            raise MapperError(f"Consultant entry missing 'id': {entry}")
        keys = [entry.get("name", ""), entry.get("email", "")] + list(entry.get("aliases", []))
        for key in keys:
            cleaned = str(key).strip()
            if cleaned:
                lookup[cleaned] = cid
    return lookup


def _build_id_name_lookup(entries: list[dict]) -> dict[str, str]:
    """Build id→canonical name lookup from structured consultant entries."""
    lookup: dict[str, str] = {}
    for entry in entries:
        cid = str(entry.get("id", "")).strip()
        name = str(entry.get("name", "")).strip()
        if cid and name:
            lookup[cid] = name
    return lookup


def load_id_name_map(path: Path) -> dict[str, str]:
    """Load ID→canonical name mapping from YAML.

    Returns a dict where every consultant ID maps to the canonical name.
    Example: {'C01': 'Anna Becker', 'C02': 'Ben Müller', ...}
    """
    if not path.exists():
        raise MapperError(f"Consultant map not found: {path}")
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise MapperError(f"Invalid YAML in {path}: {e}") from e
    if not isinstance(data, dict) or "consultants" not in data:
        raise MapperError(f"Consultant map missing 'consultants' key: {path}")
    return _build_id_name_lookup(data["consultants"])


def load_consultant_map(path: Path) -> dict[str, str]:
    """Load name/email/alias→ID mapping from YAML.

    Returns a flat dict where every registered key (name, email, alias)
    maps to the consultant ID. Example: {'Anna Becker': 'C01',
    'anna.becker@company.com': 'C01', 'Becker, Anna': 'C01', ...}
    """
    if not path.exists():
        raise MapperError(f"Consultant map not found: {path}")
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise MapperError(f"Invalid YAML in {path}: {e}") from e
    if not isinstance(data, dict):
        raise MapperError(f"Consultant map must be a dict, got {type(data).__name__}: {path}")
    if "consultants" not in data:
        raise MapperError(f"Consultant map missing 'consultants' key: {path}")
    if not isinstance(data["consultants"], list):
        raise MapperError(f"'consultants' must be a list in: {path}")
    return _build_lookup(data["consultants"])


def map_name_to_id(name: str, consultant_map: dict[str, str]) -> str:
    """Resolve a consultant full name to its anonymized ID.

    Raises MapperError if the name is not in the map.
    """
    cleaned = name.strip()
    if cleaned not in consultant_map:
        raise MapperError(f"Unknown consultant: {cleaned!r} — add to consultant_map.yaml")
    return consultant_map[cleaned]


def get_all_ids(consultant_map: dict[str, str]) -> set[str]:
    """Return the complete set of expected consultant IDs."""
    return set(consultant_map.values())


def find_missing_ids(
    submitted_names: list[str],
    consultant_map: dict[str, str],
) -> list[str]:
    """Return sorted list of IDs that have not submitted.

    Unknown names (not in map) are silently ignored — they are handled
    by the aggregator which raises on unknown names during anonymization.
    """
    submitted_ids = {
        consultant_map[name.strip()]
        for name in submitted_names
        if name.strip() in consultant_map
    }
    return sorted(get_all_ids(consultant_map) - submitted_ids)
