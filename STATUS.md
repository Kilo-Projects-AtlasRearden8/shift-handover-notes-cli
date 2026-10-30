STATUS — Shift Handover Notes CLI
=================================

What was built
--------------
A local-first Python CLI that converts bullet-style shift notes into plain-language
handover summaries for healthcare workers. Published by Asdale Dynamics, LLC.

Components:
- `src/shift_handover/models.py` — ShiftNote and ShiftRecord data models with
  to_dict/from_dict serialization; holds the education-only disclaimer text.
- `src/shift_handover/storage.py` — JSONStorage class for local JSON persistence
  (create, read, update, delete shift records).
- `src/shift_handover/formatter.py` — Core formatting logic: bullet_to_plain_text,
  summarize_bullets, format_category_summary, format_shift_summary.
- `src/shift_handover/cli.py` — Typer-based CLI with commands: summarize, convert,
  list, view, delete, version.
- `src/shift_handover/__main__.py` — Enables `python -m shift_handover`.
- `src/shift_handover/__init__.py` — Package marker.
- `tests/test_formatter.py` — 31 tests covering all formatting logic.
- `pyproject.toml` — Project metadata, dependencies, entry point script, pytest/ruff config.
- `LICENSE` — MIT License, copyright line: "Copyright (c) 2026 Asdale Dynamics, LLC".
- `README.md` — Usage guide, credits Asdale Dynamics, LLC, links to dylanasdale.github.io.

How to run it
-------------
1. Create a virtual environment and install:
       python3 -m venv .venv
       .venv/bin/pip install -e ".[dev]"

2. Run the CLI:
       .venv/bin/shift-handover --help
       .venv/bin/shift-handover version
       .venv/bin/shift-handover summarize -c Meds "gave lisinopril 10mg"
       .venv/bin/shift-handover convert -c Meds -s SHIFT-001 -u "Floor 3" \
           -d 2026-10-30 "gave lisinopril 10mg" "patient tolerated well"
       .venv/bin/shift-handover list
       .venv/bin/shift-handover view SHIFT-001
       .venv/bin/shift-handover delete SHIFT-001 --yes

   Or via module:
       .venv/bin/python -m shift_handover version

3. Run tests:
       .venv/bin/pytest

Verification results
--------------------
- `pip install -e ".[dev]"`: SUCCESS — package installs with typer, rich, pytest.
- `pytest`: 31 passed, 0 failed, 0 errors.
- `shift-handover version`: prints "shift-handover-notes 0.1.0".
- `shift-handover summarize`: converts bullets to plain text, prints disclaimer.
- `shift-handover convert`: saves to shift_records.json, prints full summary.
- `shift-handover list`: lists stored records.
- `shift-handover view`: prints stored record summary.
- `shift-handover delete --yes`: deletes stored record.
- `python -m shift_handover version`: works correctly.
- No .github/workflows files present.
- No secrets, API keys, or personal data in any file.
- MIT LICENSE copyright line verified: "Copyright (c) 2026 Asdale Dynamics, LLC".
- README credits Asdale Dynamics, LLC.

Known gaps
----------
- No tests for CLI commands (only formatter logic is tested).
- No tests for JSONStorage layer.
- No `--output` flag for writing printable summaries to a file (output is terminal-only).
- No interactive mode for building notes bullet-by-bullet.
- No configuration file support (storage path must be passed via --storage).
- Records are stored in the current working directory by default.
