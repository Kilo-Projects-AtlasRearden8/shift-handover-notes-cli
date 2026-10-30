"""CLI for shift handover notes converter."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .formatter import (
    bullet_to_plain_text,
    format_category_summary,
    format_shift_summary,
    summarize_bullets,
    DISCLAIMER,
)
from .models import ShiftNote, ShiftRecord
from .storage import JSONStorage, StorageError

app = typer.Typer(
    name="shift-handover",
    help="Convert bullet-style shift notes into plain-language handover summaries "
    "for healthcare workers (education only, not medical advice).",
    no_args_is_help=True,
)
console = Console()


@app.command()
def summarize(
    bullets: list[str] = typer.Argument(
        None, help="Bullet-style notes to convert (quoted strings)."
    ),
    category: str = typer.Option(
        "General", "--category", "-c", help="Note category label."
    ),
) -> None:
    """Convert bullet notes into a plain-language summary and print it."""
    if not bullets:
        console.print("[yellow]No bullets provided.[/yellow]")
        raise typer.Exit(code=0)

    plain = summarize_bullets(bullets)
    console.print(Panel.fit(plain, title=f"Category: {category}", border_style="green"))
    console.print(Text(DISCLAIMER.strip(), style="italic red"))


@app.command()
def convert(
    bullets: list[str] = typer.Argument(
        None, help="Bullet-style notes to convert (quoted strings)."
    ),
    category: str = typer.Option(
        "General", "--category", "-c", help="Note category label."
    ),
    shift_id: str = typer.Option(
        None, "--shift-id", "-s", help="Shift ID for the record."
    ),
    unit: str = typer.Option(
        None, "--unit", "-u", help="Hospital unit or ward."
    ),
    date: str = typer.Option(
        None, "--date", "-d", help="Shift date (YYYY-MM-DD)."
    ),
    storage_path: Path = typer.Option(
        Path("shift_records.json"), "--storage", help="JSON storage file path."
    ),
) -> None:
    """Convert bullets, save as a shift record, and print the summary."""
    from datetime import datetime

    if not bullets:
        console.print("[yellow]No bullets provided.[/yellow]")
        raise typer.Exit(code=0)

    if not shift_id:
        shift_id = f"SHIFT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if not unit:
        unit = "General"
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    record = ShiftRecord(shift_id=shift_id, unit=unit, date=date)
    record.add_note(category=category, bullets=list(bullets))

    storage = JSONStorage(storage_path)
    try:
        storage.save_record(record)
    except StorageError as e:
        console.print(f"[red]Storage error: {e}[/red]")
        raise typer.Exit(code=1)

    summary = format_shift_summary(record)
    console.print(summary)


@app.command(name="list")
def list_records(
    storage_path: Path = typer.Option(
        Path("shift_records.json"), "--storage", help="JSON storage file path."
    ),
) -> None:
    """List all stored shift records."""
    storage = JSONStorage(storage_path)
    try:
        records = storage.list_records()
    except StorageError as e:
        console.print(f"[red]Storage error: {e}[/red]")
        raise typer.Exit(code=1)

    if not records:
        console.print("[yellow]No records found.[/yellow]")
        return

    for r in records:
        console.print(
            f"[bold]{r.shift_id}[/bold] | {r.unit} | {r.date} | "
            f"{len(r.notes)} note category/categories"
        )


@app.command()
def view(
    shift_id: str = typer.Argument(..., help="Shift ID to view."),
    storage_path: Path = typer.Option(
        Path("shift_records.json"), "--storage", help="JSON storage file path."
    ),
) -> None:
    """View the plain-language summary for a stored shift record."""
    storage = JSONStorage(storage_path)
    try:
        record = storage.get_record(shift_id)
    except StorageError as e:
        console.print(f"[red]Storage error: {e}[/red]")
        raise typer.Exit(code=1)

    if record is None:
        console.print(f"[yellow]No record found for shift ID: {shift_id}[/yellow]")
        raise typer.Exit(code=0)

    console.print(format_shift_summary(record))


@app.command()
def delete(
    shift_id: str = typer.Argument(..., help="Shift ID to delete."),
    storage_path: Path = typer.Option(
        Path("shift_records.json"), "--storage", help="JSON storage file path."
    ),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """Delete a stored shift record."""
    storage = JSONStorage(storage_path)
    if not confirm:
        confirm_delete = typer.confirm(f"Delete shift record '{shift_id}'?")
        if not confirm_delete:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=0)

    try:
        deleted = storage.delete_record(shift_id)
    except StorageError as e:
        console.print(f"[red]Storage error: {e}[/red]")
        raise typer.Exit(code=1)

    if deleted:
        console.print(f"[green]Deleted shift record '{shift_id}'.[/green]")
    else:
        console.print(f"[yellow]No record found for shift ID: {shift_id}[/yellow]")


@app.command()
def version() -> None:
    """Show the version."""
    console.print("shift-handover-notes 0.1.0")


if __name__ == "__main__":
    app()
