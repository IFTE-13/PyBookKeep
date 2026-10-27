"""Utility functions for PyLibrary CLI.

Provides text formatting, table rendering, validated input readers,
and UI helpers for terminal displays.
"""

import os
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform manner."""
    # Only clear if terminal is attached
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def print_banner(title: str, subtitle: Optional[str] = None) -> None:
    """Display a formatted section banner."""
    width = 72
    print()
    print("=" * width)
    print(f" {title.upper()} ".center(width, " "))
    if subtitle:
        print(f" {subtitle} ".center(width, " "))
    print("=" * width)
    print()


def print_header(text: str) -> None:
    """Display a secondary section header."""
    width = 72
    print()
    print(f"--- {text} ---")
    print("-" * max(len(text) + 8, 30))


def print_success(message: str) -> None:
    """Display a success message."""
    print(f"\n[SUCCESS] {message}")


def print_warning(message: str) -> None:
    """Display a warning message."""
    print(f"\n[WARNING] {message}")


def print_error(message: str) -> None:
    """Display an error message."""
    print(f"\n[ERROR] {message}")


def print_info(message: str) -> None:
    """Display an informational message."""
    print(f"\n[INFO] {message}")


def pause() -> None:
    """Wait for the user to press Enter to continue."""
    try:
        input("\nPress Enter to continue...")
    except (KeyboardInterrupt, EOFError):
        print()


def get_non_empty_input(prompt: str, allow_cancel: bool = True) -> Optional[str]:
    """Prompt the user for a non-empty string.

    If allow_cancel is True and user types 'cancel' (case-insensitive), returns None.
    """
    while True:
        try:
            value = input(prompt).strip()
            if allow_cancel and value.lower() == "cancel":
                return None
            if value:
                return value
            print("  Input cannot be empty. Please try again (or type 'cancel').")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return None


def get_int_input(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    allow_cancel: bool = True,
) -> Optional[int]:
    """Prompt the user for an integer within an optional range."""
    while True:
        try:
            raw = input(prompt).strip()
            if allow_cancel and raw.lower() == "cancel":
                return None
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"  Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  Value cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("  Invalid number. Please enter an integer (or type 'cancel').")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return None


def get_confirmation(prompt: str, default_yes: bool = True) -> bool:
    """Prompt user with a Yes/No question."""
    suffix = " [Y/n]: " if default_yes else " [y/N]: "
    try:
        choice = input(prompt + suffix).strip().lower()
        if not choice:
            return default_yes
        return choice in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        return False


def format_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    max_col_width: int = 30,
) -> str:
    """Render a clean, aligned text table from headers and row data.

    Handles column truncation and proper spacing for clean terminal output.
    """
    if not headers:
        return "No data to display."

    # Convert all cells to strings and truncate if longer than max_col_width
    def format_cell(cell: Any, max_w: int) -> str:
        s = str(cell) if cell is not None else ""
        if len(s) > max_w:
            return s[: max_w - 3] + "..."
        return s

    str_rows: List[List[str]] = []
    for row in rows:
        str_rows.append([format_cell(cell, max_col_width) for cell in row])

    # Determine column widths
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(cell))
            else:
                col_widths.append(len(cell))

    # Pad widths slightly
    col_widths = [w + 2 for w in col_widths]

    # Build border
    separator = "+" + "+".join("-" * w for w in col_widths) + "+"

    # Build header row
    header_line = "|" + "|".join(f" {h} ".ljust(col_widths[i]) for i, h in enumerate(headers)) + "|"

    lines = [separator, header_line, separator]

    if not str_rows:
        empty_line = "|" + "No records found".center(sum(col_widths) + len(col_widths) - 1) + "|"
        lines.append(empty_line)
    else:
        for row in str_rows:
            # Ensure row matches number of columns
            padded_row = list(row) + [""] * (len(col_widths) - len(row))
            row_line = "|" + "|".join(f" {padded_row[i]} ".ljust(col_widths[i]) for i in range(len(col_widths))) + "|"
            lines.append(row_line)

    lines.append(separator)
    return "\n".join(lines)
