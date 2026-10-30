"""JSON storage for shift handover records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ShiftRecord, ShiftNote


class StorageError(Exception):
    """Raised when storage operations fail."""

    pass


class JSONStorage:
    """Local JSON file storage for shift records."""

    def __init__(self, storage_path: Path | str = "shift_records.json"):
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage file if it doesn't exist."""
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({"records": []}, indent=2))

    def _load_data(self) -> dict[str, Any]:
        """Load and parse the storage file."""
        try:
            content = self.storage_path.read_text(encoding="utf-8")
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in storage file: {e}") from e
        except OSError as e:
            raise StorageError(f"Failed to read storage file: {e}") from e

    def _save_data(self, data: dict[str, Any]) -> None:
        """Save data to storage file."""
        try:
            self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError as e:
            raise StorageError(f"Failed to write storage file: {e}") from e

    def list_records(self) -> list[ShiftRecord]:
        """Return all shift records."""
        data = self._load_data()
        return [ShiftRecord.from_dict(r) for r in data.get("records", [])]

    def get_record(self, shift_id: str) -> ShiftRecord | None:
        """Get a specific shift record by ID."""
        records = self.list_records()
        for record in records:
            if record.shift_id == shift_id:
                return record
        return None

    def save_record(self, record: ShiftRecord) -> None:
        """Save or update a shift record."""
        data = self._load_data()
        records = data.get("records", [])

        # Check if record exists
        for i, existing in enumerate(records):
            if existing.get("shift_id") == record.shift_id:
                records[i] = record.to_dict()
                self._save_data({"records": records})
                return

        # Add new record
        records.append(record.to_dict())
        self._save_data({"records": records})

    def delete_record(self, shift_id: str) -> bool:
        """Delete a shift record by ID. Returns True if deleted."""
        data = self._load_data()
        records = data.get("records", [])
        original_len = len(records)
        records = [r for r in records if r.get("shift_id") != shift_id]
        if len(records) < original_len:
            self._save_data({"records": records})
            return True
        return False