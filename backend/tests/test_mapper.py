"""Tests for mapper.py — name→ID resolution and missing detection."""

import pytest
import yaml
from pathlib import Path

from mapper import (
    load_consultant_map, load_id_name_map, map_name_to_id, get_all_ids,
    find_missing_ids, MapperError,
)


# ---------------------------------------------------------------------------
# load_consultant_map
# ---------------------------------------------------------------------------

def test_load_consultant_map_success(tmp_path, consultant_map_yaml):
    path = tmp_path / "consultant_map.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(consultant_map_yaml, f, allow_unicode=True)
    result = load_consultant_map(path)
    # primary name lookup
    assert result["Anna Becker"] == "C01"
    # email lookup
    assert result["anna.becker@example.com"] == "C01"
    # alias lookup
    assert result["Becker, Anna"] == "C01"
    # all 17 IDs represented (3 keys per consultant = 51 entries)
    assert len(set(result.values())) == 17


def test_load_consultant_map_not_found():
    with pytest.raises(MapperError, match="not found"):
        load_consultant_map(Path("/nonexistent/map.yaml"))


def test_load_consultant_map_invalid_yaml(tmp_path):
    path = tmp_path / "map.yaml"
    path.write_text("[\ninvalid yaml: {\n")
    with pytest.raises(MapperError, match="Invalid YAML"):
        load_consultant_map(path)


def test_load_consultant_map_wrong_type(tmp_path):
    path = tmp_path / "map.yaml"
    path.write_text("- item1\n- item2\n")
    with pytest.raises(MapperError, match="must be a dict"):
        load_consultant_map(path)


def test_load_consultant_map_missing_consultants_key(tmp_path):
    path = tmp_path / "map.yaml"
    path.write_text("other_key: value\n")
    with pytest.raises(MapperError, match="missing 'consultants' key"):
        load_consultant_map(path)


def test_load_consultant_map_strips_whitespace(tmp_path):
    path = tmp_path / "map.yaml"
    path.write_text(
        "consultants:\n"
        "  - id: '  C01  '\n"
        "    name: '  Anna Becker  '\n"
        "    email: '  anna.becker@example.com  '\n"
        "    aliases: []\n"
    )
    result = load_consultant_map(path)
    assert "Anna Becker" in result
    assert result["Anna Becker"] == "C01"
    assert result["anna.becker@example.com"] == "C01"


# ---------------------------------------------------------------------------
# load_id_name_map
# ---------------------------------------------------------------------------

def test_load_id_name_map_success(tmp_path, consultant_map_yaml):
    path = tmp_path / "consultant_map.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(consultant_map_yaml, f, allow_unicode=True)
    result = load_id_name_map(path)
    assert result["C01"] == "Anna Becker"
    assert result["C17"] == "Quin Hoffmann"
    assert len(result) == 17


def test_load_id_name_map_not_found():
    with pytest.raises(MapperError, match="not found"):
        load_id_name_map(Path("/nonexistent/map.yaml"))


def test_load_id_name_map_invalid_yaml(tmp_path):
    path = tmp_path / "map.yaml"
    path.write_text("[\ninvalid yaml: {\n")
    with pytest.raises(MapperError, match="Invalid YAML"):
        load_id_name_map(path)


# ---------------------------------------------------------------------------
# map_name_to_id
# ---------------------------------------------------------------------------

def test_map_name_to_id_success(consultant_map):
    assert map_name_to_id("Anna Becker", consultant_map) == "C01"
    assert map_name_to_id("Quin Hoffmann", consultant_map) == "C17"


def test_map_name_to_id_strips_whitespace(consultant_map):
    assert map_name_to_id("  Anna Becker  ", consultant_map) == "C01"


def test_map_name_to_id_unknown_name(consultant_map):
    with pytest.raises(MapperError, match="Unknown consultant"):
        map_name_to_id("Unknown Person", consultant_map)


def test_map_name_to_id_empty_name(consultant_map):
    with pytest.raises(MapperError, match="Unknown consultant"):
        map_name_to_id("", consultant_map)


# ---------------------------------------------------------------------------
# get_all_ids
# ---------------------------------------------------------------------------

def test_get_all_ids_returns_all(consultant_map):
    ids = get_all_ids(consultant_map)
    assert len(ids) == 17
    assert "C01" in ids
    assert "C17" in ids


# ---------------------------------------------------------------------------
# find_missing_ids
# ---------------------------------------------------------------------------

def test_find_missing_ids_all_present(consultant_map):
    submitted = list(consultant_map.keys())
    missing = find_missing_ids(submitted, consultant_map)
    assert missing == []


def test_find_missing_ids_some_missing(consultant_map):
    submitted = ["Anna Becker", "Ben Müller"]
    missing = find_missing_ids(submitted, consultant_map)
    assert "C01" not in missing
    assert "C02" not in missing
    assert len(missing) == 15


def test_find_missing_ids_returns_sorted(consultant_map):
    submitted = list(consultant_map.keys())[:10]
    missing = find_missing_ids(submitted, consultant_map)
    assert missing == sorted(missing)


def test_find_missing_ids_unknown_names_ignored(consultant_map):
    submitted = list(consultant_map.keys()) + ["Unknown Ghost"]
    missing = find_missing_ids(submitted, consultant_map)
    assert missing == []


def test_find_missing_ids_all_missing(consultant_map):
    missing = find_missing_ids([], consultant_map)
    assert len(missing) == 17
