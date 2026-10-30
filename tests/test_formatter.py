"""Tests for shift handover formatting logic."""

import pytest

from shift_handover.formatter import (
    bullet_to_plain_text,
    format_category_summary,
    format_shift_summary,
    summarize_bullets,
    DISCLAIMER,
)
from shift_handover.models import ShiftNote, ShiftRecord


class TestBulletToPlainText:
    """Tests for bullet_to_plain_text."""

    def test_plain_bullet_no_marker(self):
        assert bullet_to_plain_text("patient stable") == "Patient stable."

    def test_bullet_with_dash(self):
        assert bullet_to_plain_text("- patient stable") == "Patient stable."

    def test_bullet_with_asterisk(self):
        assert bullet_to_plain_text("* patient stable") == "Patient stable."

    def test_bullet_with_bullet_char(self):
        assert bullet_to_plain_text("• patient stable") == "Patient stable."

    def test_bullet_with_en_dash(self):
        assert bullet_to_plain_text("– patient stable") == "Patient stable."

    def test_bullet_already_capitalized(self):
        assert bullet_to_plain_text("Patient stable") == "Patient stable."

    def test_bullet_with_period(self):
        assert bullet_to_plain_text("Patient stable.") == "Patient stable."

    def test_bullet_with_existing_period_no_double(self):
        assert bullet_to_plain_text("Patient stable.") == "Patient stable."

    def test_empty_bullet(self):
        assert bullet_to_plain_text("") == ""

    def test_whitespace_only_bullet(self):
        assert bullet_to_plain_text("   ") == ""

    def test_bullet_with_leading_whitespace(self):
        assert bullet_to_plain_text("  patient stable  ") == "Patient stable."

    def test_bullet_multiple_sentences(self):
        assert bullet_to_plain_text("patient stable. vitals normal.") == "Patient stable. vitals normal."

    def test_bullet_ends_with_question(self):
        assert bullet_to_plain_text("any questions?") == "Any questions?"

    def test_bullet_ends_with_exclamation(self):
        assert bullet_to_plain_text("call doctor!") == "Call doctor!"


class TestSummarizeBullets:
    """Tests for summarize_bullets."""

    def test_empty_list(self):
        assert summarize_bullets([]) == ""

    def test_single_bullet(self):
        assert summarize_bullets(["- patient stable"]) == "Patient stable."

    def test_multiple_bullets(self):
        result = summarize_bullets(["- patient stable", "* vitals normal"])
        assert "Patient stable." in result
        assert "Vitals normal." in result

    def test_filters_empty_bullets(self):
        result = summarize_bullets(["- patient stable", "", "   ", "* vitals normal"])
        assert "Patient stable." in result
        assert "Vitals normal." in result
        assert result.count("\n") == 1


class TestFormatCategorySummary:
    """Tests for format_category_summary."""

    def test_empty_notes(self):
        assert format_category_summary("General", []) == ""

    def test_notes_with_no_bullets(self):
        note = ShiftNote(category="General", bullets=[])
        assert format_category_summary("General", [note]) == ""

    def test_single_note_single_bullet(self):
        note = ShiftNote(category="General", bullets=["- patient stable"])
        result = format_category_summary("General", [note])
        assert "**General**" in result
        assert "1. Patient stable." in result

    def test_multiple_notes_same_category(self):
        n1 = ShiftNote(category="Meds", bullets=["- gave lisinopril 10mg"])
        n2 = ShiftNote(category="Meds", bullets=["- gave metoprolol 25mg"])
        result = format_category_summary("Meds", [n1, n2])
        assert "**Meds**" in result
        assert "1. Gave lisinopril 10mg." in result
        assert "2. Gave metoprolol 25mg." in result

    def test_multiple_categories_not_mixed(self):
        n1 = ShiftNote(category="Meds", bullets=["- gave lisinopril"])
        n2 = ShiftNote(category="Vitals", bullets=["- bp 120/80"])
        meds = format_category_summary("Meds", [n1])
        vitals = format_category_summary("Vitals", [n2])
        assert "**Meds**" in meds
        assert "**Vitals**" in vitals
        assert "bp" not in meds.lower()
        assert "lisinopril" not in vitals.lower()


class TestFormatShiftSummary:
    """Tests for format_shift_summary."""

    def test_empty_record(self):
        record = ShiftRecord(shift_id="S1", unit="ICU", date="2026-01-01")
        result = format_shift_summary(record)
        assert "SHIFT HANDOVER SUMMARY" in result
        assert "S1" in result
        assert "ICU" in result
        assert "2026-01-01" in result
        assert "No notes recorded" in result
        assert DISCLAIMER.strip() in result
        assert "END OF SUMMARY" in result

    def test_record_with_notes(self):
        n1 = ShiftNote(category="Meds", bullets=["- gave lisinopril 10mg"])
        record = ShiftRecord(
            shift_id="S2", unit="Floor 3", date="2026-01-02", notes=[n1]
        )
        result = format_shift_summary(record)
        assert "S2" in result
        assert "Floor 3" in result
        assert "**Meds**" in result
        assert "Gave lisinopril 10mg." in result
        assert DISCLAIMER.strip() in result

    def test_disclaimer_always_present(self):
        record = ShiftRecord(shift_id="S3", unit="ER", date="2026-01-03")
        result = format_shift_summary(record)
        assert "NOT medical advice" in result
        assert "EDUCATIONAL PURPOSES ONLY" in result

    def test_created_and_updated_timestamps(self):
        record = ShiftRecord(shift_id="S4", unit="ICU", date="2026-01-04")
        result = format_shift_summary(record)
        assert "Created:" in result

    def test_dash_separator_present(self):
        record = ShiftRecord(shift_id="S5", unit="ICU", date="2026-01-05")
        result = format_shift_summary(record)
        assert "=" * 60 in result
        assert "-" * 60 in result


class TestDisclaimer:
    """Tests for the education disclaimer."""

    def test_disclaimer_contains_not_medical_advice(self):
        assert "NOT medical advice" in DISCLAIMER

    def test_disclaimer_contains_educational(self):
        assert "EDUCATIONAL PURPOSES ONLY" in DISCLAIMER

    def test_disclaimer_non_empty(self):
        assert len(DISCLAIMER) > 0
