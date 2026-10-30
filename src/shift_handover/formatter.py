"""Formatting logic: convert bullet-style shift notes into plain-language summaries."""

from __future__ import annotations

from typing import Any

from .models import ShiftNote, ShiftRecord, DISCLAIMER


def bullet_to_plain_text(bullet: str) -> str:
    """Convert a single bullet into plain-language sentence form.

    Strips leading dash/bullet markers, trims whitespace, capitalizes the
    first letter, and ensures a trailing period.
    """
    text = bullet.strip()
    # Remove leading bullet markers (-, *, •, –)
    if text and text[0] in "-*•–":
        text = text[1:].strip()
    if not text:
        return ""
    # Capitalize first letter
    text = text[0].upper() + text[1:]
    # Ensure trailing period
    if text and not text[-1] in ".!?":
        text += "."
    return text


def format_category_summary(category: str, notes: list[ShiftNote]) -> str:
    """Format all bullets in a category into a plain-language paragraph.

    Returns an empty string if there are no bullets across all notes.
    """
    bullets: list[str] = []
    for note in notes:
        for b in note.bullets:
            plain = bullet_to_plain_text(b)
            if plain:
                bullets.append(plain)

    if not bullets:
        return ""

    lines = [f"**{category}**"]
    for i, b in enumerate(bullets, start=1):
        lines.append(f"  {i}. {b}")
    lines.append("")
    return "\n".join(lines)


def format_shift_summary(record: ShiftRecord) -> str:
    """Build a full plain-language handover summary from a ShiftRecord.

    Includes header info, category-by-category plain-language summaries,
    and the education-only disclaimer at the end.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("SHIFT HANDOVER SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Shift ID:    {record.shift_id}")
    lines.append(f"Unit:        {record.unit}")
    lines.append(f"Date:        {record.date}")
    lines.append(f"Created:     {record.created_at}")
    if record.updated_at != record.created_at:
        lines.append(f"Updated:     {record.updated_at}")
    lines.append("-" * 60)
    lines.append("")

    if not record.notes:
        lines.append("No notes recorded for this shift.")
        lines.append("")
    else:
        seen_categories: list[str] = []
        for note in record.notes:
            if note.category not in seen_categories:
                seen_categories.append(note.category)

        for cat in seen_categories:
            cat_notes = record.get_notes_by_category(cat)
            section = format_category_summary(cat, cat_notes)
            if section:
                lines.append(section)

    lines.append(DISCLAIMER.strip())
    lines.append("=" * 60)
    lines.append("END OF SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def summarize_bullets(bullets: list[str]) -> str:
    """Standalone helper: convert a list of bullets to plain text lines.

    Useful for testing formatting logic in isolation.
    """
    result: list[str] = []
    for b in bullets:
        plain = bullet_to_plain_text(b)
        if plain:
            result.append(plain)
    return "\n".join(result)


__all__ = [
    "bullet_to_plain_text",
    "format_category_summary",
    "format_shift_summary",
    "summarize_bullets",
    "DISCLAIMER",
]
