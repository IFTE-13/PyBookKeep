"""Borrowing and return management module for Simple Library Management System.

Handles checkout workflows, inventory copy tracking, return timestamps,
and complete persistent borrow history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import books as books_mod
import storage
import utils

BORROWING_FILE = "borrowing_records.json"
MAX_BORROW_LIMIT = 3


def load_borrowing_records(data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load borrowing records from storage."""
    file_path = storage.get_data_path(BORROWING_FILE, data_dir)
    storage.initialize_file_if_missing(file_path, [])
    return storage.load_json(file_path, default_data=[])


def save_borrowing_records(records: List[Dict[str, Any]], data_dir: Optional[str] = None) -> None:
    """Save borrowing records to storage."""
    file_path = storage.get_data_path(BORROWING_FILE, data_dir)
    storage.save_json(file_path, records)


def get_active_borrowings(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return all currently active (unreturned) borrowing records."""
    return [r for r in records if r.get("status") in ("active", "Borrowed")]


def get_active_borrowings_for_user(
    username_or_id: str, records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Return active borrowings for a specific user or student ID."""
    target = str(username_or_id).strip().lower()
    return [
        r for r in records
        if (
            str(r.get("student_id", "")).strip().lower() == target
            or str(r.get("username", "")).strip().lower() == target
        )
        and r.get("status") in ("active", "Borrowed")
    ]


def get_borrow_history(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return full borrowing history, sorted by borrow date descending."""
    return sorted(
        records,
        key=lambda r: r.get("borrow_date", ""),
        reverse=True,
    )


def get_borrowings_for_student(
    student_id: str, records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Return all borrowing records for a specific student."""
    sid = str(student_id).strip().lower()
    return [
        r for r in records
        if (
            str(r.get("student_id", "")).strip().lower() == sid
            or str(r.get("username", "")).strip().lower() == sid
        )
    ]


def borrow_book(
    student_id: str = "",
    book_id: str = "",
    books: Optional[List[Dict[str, Any]]] = None,
    *extra_args,
    students: Optional[List[Dict[str, Any]]] = None,
    records: Optional[List[Dict[str, Any]]] = None,
    data_dir: Optional[str] = None,
    **kwargs,
) -> Tuple[bool, str]:
    """Process a book checkout for a student.

    Supports positional or keyword calling forms:
      borrow_book(student_id, book_id, books, students, records, data_dir)
      borrow_book(student_id, book_id, books, records, data_dir)
      borrow_book(student_id=..., book_id=..., books=..., students=..., records=...)
    """
    clean_sid = str(student_id or kwargs.get("username", "")).strip()
    clean_bid = str(book_id).strip()

    if books is None:
        books = []

    # Unpack extra positional args
    if extra_args:
        if len(extra_args) == 1:
            records = extra_args[0]
        elif len(extra_args) >= 2:
            students = extra_args[0]
            records = extra_args[1]
            if len(extra_args) >= 3 and data_dir is None:
                data_dir = extra_args[2]

    actual_records = records if records is not None else []
    actual_students = students if students is not None else []

    if not clean_sid:
        return False, "Student ID cannot be empty."

    student_name = clean_sid
    for s in actual_students:
        if str(s.get("id", "")).strip().lower() == clean_sid.lower():
            student_name = s.get("name", clean_sid)
            break

    # Check max borrow limit
    active_borrows = get_active_borrowings_for_user(clean_sid, actual_records)
    if len(active_borrows) >= MAX_BORROW_LIMIT:
        return (
            False,
            f"Borrow limit reached! Student already has {len(active_borrows)} books borrowed. "
            f"Maximum limit is {MAX_BORROW_LIMIT}.",
        )

    # Check book
    book = books_mod.find_book_by_id(clean_bid, books)
    if not book:
        return False, f"Book with ID '{clean_bid}' does not exist in the catalog."

    avail_copies = int(book.get("available_copies", 1 if book.get("available", True) else 0))
    if avail_copies <= 0 or not book.get("available", True):
        return False, f"Book '{book.get('title')}' is currently unavailable. All copies given away."

    # Prevent duplicate active borrow of exact same book by same student
    for rec in actual_records:
        rec_sid = str(rec.get("student_id", rec.get("username", ""))).strip().lower()
        rec_bid = str(rec.get("book_id", "")).strip().lower()
        if rec_sid == clean_sid.lower() and rec_bid == clean_bid.lower() and rec.get("status") in ("active", "Borrowed"):
            return False, f"Conflict: Book '{book['id']}' already has an active borrow record for this student."

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record_id = f"REC-{len(actual_records) + 1:04d}"

    # Decrement available copies
    book["available_copies"] = max(0, avail_copies - 1)
    book["available"] = book["available_copies"] > 0

    new_record = {
        "record_id": record_id,
        "username": clean_sid,
        "student_id": clean_sid,
        "student_name": student_name,
        "book_id": book["id"],
        "book_title": book.get("title", "Unknown"),
        "borrow_date": timestamp_str,
        "return_date": None,
        "status": "active",
    }
    actual_records.append(new_record)

    books_mod.save_books(books, data_dir)
    save_borrowing_records(actual_records, data_dir)

    return (
        True,
        f"Success! You have borrowed '{book.get('title')}' (ID: {book['id']}). Record ID: {record_id}.",
    )


def return_book_by_record(
    record_id: str,
    books: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Process a book return using its unique borrow record ID."""
    clean_rid = str(record_id).strip().lower()
    target_record: Optional[Dict[str, Any]] = None

    for rec in records:
        if str(rec.get("record_id", "")).strip().lower() == clean_rid:
            target_record = rec
            break

    if not target_record:
        return False, f"Borrow record '{record_id}' not found."

    if target_record.get("status") not in ("active", "Borrowed"):
        return False, f"Record '{record_id}' is already marked as returned on {target_record.get('return_date')}."

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_record["return_date"] = timestamp_str
    target_record["status"] = "returned"

    # Increment available copies on book
    book = books_mod.find_book_by_id(target_record["book_id"], books)
    if book:
        total = int(book.get("total_copies", 1))
        avail = int(book.get("available_copies", 0))
        book["available_copies"] = min(total, avail + 1)
        book["available"] = book["available_copies"] > 0
        books_mod.save_books(books, data_dir)

    save_borrowing_records(records, data_dir)

    book_title = target_record.get("book_title", target_record.get("book_id"))
    student_name = target_record.get("student_name", target_record.get("student_id", "Student"))
    return (
        True,
        f"Success! Book '{book_title}' has been returned by {student_name} on {timestamp_str}.",
    )


def return_book(
    student_id: str,
    book_id: str,
    books: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Process a book return matching student ID and book ID."""
    clean_sid = str(student_id).strip().lower()
    clean_bid = str(book_id).strip().lower()

    for rec in records:
        rec_sid = str(rec.get("student_id", rec.get("username", ""))).strip().lower()
        rec_bid = str(rec.get("book_id", "")).strip().lower()
        if rec_sid == clean_sid and rec_bid == clean_bid and rec.get("status") in ("active", "Borrowed"):
            return return_book_by_record(rec["record_id"], books, records, data_dir)

    return False, f"No active borrowing record found for user '{student_id}' and book '{book_id}'."


def render_borrowings_table(records: List[Dict[str, Any]], active_only: bool = False) -> str:
    """Format borrow records into an ASCII table."""
    to_display = get_active_borrowings(records) if active_only else records
    headers = ["Record ID", "Book ID", "Title", "Student ID", "Student Name", "Borrow Date", "Return Date", "Status"]
    rows = []
    for r in to_display:
        status_label = "Active" if r.get("status") in ("active", "Borrowed") else "Returned"
        rows.append([
            r.get("record_id", ""),
            r.get("book_id", ""),
            r.get("book_title", ""),
            r.get("student_id", r.get("username", "")),
            r.get("student_name", "N/A"),
            r.get("borrow_date", ""),
            r.get("return_date") or "-",
            status_label,
        ])
    return utils.format_table(headers, rows, max_col_width=22)
