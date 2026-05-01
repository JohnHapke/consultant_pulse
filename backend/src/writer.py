"""Writes aggregated output models to JSON files.

Files are named by period:
  Weekly:  pulse_2026-W15.json
  Monthly: pulse_2026-04.json

After each write, index.json is updated so the frontend can resolve
the latest file without hardcoded filenames.
"""

import json
from pathlib import Path

from models import WeeklyPulseOutput, MonthlyPulseOutput


class WriterError(Exception):
    pass


def _ensure_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise WriterError(f"Cannot create output directory {path}: {e}") from e


def _write_json(data: dict, path: Path) -> None:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise WriterError(f"Cannot write {path}: {e}") from e


def _update_index(output_dir: Path, kind: str, filename: str) -> None:
    """Update index.json after writing a period file.

    Maintains sorted lists of all weekly/monthly files and sets latest_* keys.
    The frontend reads index.json to discover current and historical data.
    """
    index_path = output_dir / "index.json"
    index: dict = {}
    if index_path.exists():
        try:
            with index_path.open(encoding="utf-8") as f:
                index = json.load(f)
        except (json.JSONDecodeError, OSError):
            index = {}

    files = set(index.get(kind, []))
    files.add(filename)
    sorted_files = sorted(files, reverse=True)  # newest first (lexicographic on YYYY-WNN/YYYY-MM)

    index[kind] = sorted_files
    index[f"latest_{kind}"] = sorted_files[0]

    _write_json(index, index_path)


def write_weekly(output: WeeklyPulseOutput, output_dir: Path) -> Path:
    """Serialize WeeklyPulseOutput to JSON and update index. Returns file path."""
    _ensure_dir(output_dir)
    filename = f"pulse_{output.week}.json"
    path = output_dir / filename
    _write_json(output.model_dump(mode="json"), path)
    _update_index(output_dir, "weekly", filename)
    return path


def write_monthly(output: MonthlyPulseOutput, output_dir: Path) -> Path:
    """Serialize MonthlyPulseOutput to JSON and update index. Returns file path."""
    _ensure_dir(output_dir)
    filename = f"pulse_{output.month}.json"
    path = output_dir / filename
    _write_json(output.model_dump(mode="json"), path)
    _update_index(output_dir, "monthly", filename)
    return path
