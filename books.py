"""Books management module for Simple Library Management System.

Manages book catalog data structures, search, sorting, copy inventory,
and copy availability status ("Available" vs "All copies given away").
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import storage
import utils

BOOKS_FILE = "books.json"


def get_default_books() -> List[Dict[str, Any]]:
    """Return default seed books for initial setup."""
    return [
        {
            "id": "B101",
            "title": "Automate the Boring Stuff with Python",
            "author": "Al Sweigart",
            "category": "Programming",
            "year": 2019,
            "total_copies": 3,
            "available_copies": 3,
            "available": True,
        },
        {
            "id": "B102",
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "category": "Programming",
            "year": 2023,
            "total_copies": 2,
            "available_copies": 2,
            "available": True,
        },
        {
            "id": "B103",
            "title": "Fluent Python",
            "author": "Luciano Ramalho",
            "category": "Advanced Python",
            "year": 2022,
            "total_copies": 3,
            "available_copies": 3,
            "available": True,
        },
        {
            "id": "B104",
            "title": "Introduction to Algorithms",
            "author": "Thomas H. Cormen",
            "category": "Computer Science",
            "year": 2022,
            "total_copies": 4,
            "available_copies": 4,
            "available": True,
        },
        {
            "id": "B105",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "category": "Software Engineering",
            "year": 2008,
            "total_copies": 3,
            "available_copies": 3,
            "available": True,
        },
        {
            "id": "B106",
            "title": "Head First Design Patterns",
            "author": "Eric Freeman",
            "category": "Software Engineering",
            "year": 2020,
            "total_copies": 2,
            "available_copies": 2,
            "available": True,
        },
        {
            "id": "B107",
            "title": "Python for Data Analysis",
            "author": "Wes McKinney",
            "category": "Data Science",
            "year": 2022,
            "total_copies": 2,
            "available_copies": 2,
            "available": True,
        },
        {
            "id": "B108",
            "title": "Operating System Concepts",
            "author": "Abraham Silberschatz",
            "category": "Computer Science",
            "year": 2018,
            "total_copies": 3,
            "available_copies": 3,
            "available": True,
        },
    ]


def load_books(data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load the book collection from storage. Initializes default books if missing."""
    file_path = storage.get_data_path(BOOKS_FILE, data_dir)
    storage.initialize_file_if_missing(file_path, get_default_books())
    books = storage.load_json(file_path, default_data=[])

    # Ensure backward-compatibility with copy counts
    changed = False
    for book in books:
        if "total_copies" not in book:
            book["total_copies"] = 1
            changed = True
        if "available_copies" not in book:
            book["available_copies"] = book["total_copies"] if book.get("available", True) else 0
            changed = True
        book["available"] = book["available_copies"] > 0

    if changed:
        save_books(books, data_dir)

    return books


def save_books(books: List[Dict[str, Any]], data_dir: Optional[str] = None) -> None:
    """Save the book collection to storage."""
    file_path = storage.get_data_path(BOOKS_FILE, data_dir)
    storage.save_json(file_path, books)


def get_book_status(book: Dict[str, Any]) -> str:
    """Return human-readable book status.

    Returns 'Available (X/Y)' or 'All copies given away'.
    """
    total = int(book.get("total_copies", 1))
    avail = int(book.get("available_copies", 0))
    if avail <= 0:
        return "All copies given away"
    return f"Available ({avail}/{total})"


def validate_book_data(
    book_id: str,
    title: str,
    author: str,
    category: str,
    year: int,
    total_copies: int = 1,
    existing_books: Optional[List[Dict[str, Any]]] = None,
    current_book_id: Optional[str] = None,
) -> Tuple[bool, str]:
    """Validate book fields. Returns (is_valid, error_message)."""
    if not book_id or not str(book_id).strip():
        return False, "Book ID cannot be empty."

    book_id_clean = str(book_id).strip()

    # Check for duplicate ID
    if existing_books:
        for b in existing_books:
            if b.get("id") == book_id_clean and b.get("id") != current_book_id:
                return False, f"A book with ID '{book_id_clean}' already exists."

    if not title or not str(title).strip():
        return False, "Title cannot be empty."

    if not author or not str(author).strip():
        return False, "Author cannot be empty."

    if not category or not str(category).strip():
        return False, "Category cannot be empty."

    current_year = datetime.now().year
    if not isinstance(year, int) or year < 1000 or year > current_year + 1:
        return False, f"Publication year must be between 1000 and {current_year + 1}."

    if not isinstance(total_copies, int) or total_copies < 1:
        return False, "Total copies must be at least 1."

    return True, ""


def find_book_by_id(book_id: str, books: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find and return a book by its unique ID, or None if not found."""
    target = str(book_id).strip().lower()
    for book in books:
        if str(book.get("id", "")).strip().lower() == target:
            return book
    return None


def search_books(
    books: List[Dict[str, Any]],
    query: str,
    field: str = "all",
) -> List[Dict[str, Any]]:
    """Search books by title, author, category, or across all three fields."""
    q = query.strip().lower()
    if not q:
        return list(books)

    results: List[Dict[str, Any]] = []
    for book in books:
        title = str(book.get("title", "")).lower()
        author = str(book.get("author", "")).lower()
        category = str(book.get("category", "")).lower()

        if field == "title" and q in title:
            results.append(book)
        elif field == "author" and q in author:
            results.append(book)
        elif field == "category" and q in category:
            results.append(book)
        elif field == "all":
            if q in title or q in author or q in category:
                results.append(book)

    return results


def filter_books_by_availability(
    books: List[Dict[str, Any]],
    available_only: Optional[bool] = True,
) -> List[Dict[str, Any]]:
    """Filter books by availability."""
    if available_only is None:
        return list(books)
    if available_only:
        return [b for b in books if int(b.get("available_copies", 0)) > 0]
    return [b for b in books if int(b.get("available_copies", 0)) == 0]


def sort_books(
    books: List[Dict[str, Any]],
    by: str = "title",
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Sort books by 'title', 'year', 'author', or 'id'."""
    if by == "year":
        return sorted(books, key=lambda b: (b.get("year", 0), b.get("title", "").lower()), reverse=reverse)
    elif by == "author":
        return sorted(books, key=lambda b: b.get("author", "").lower(), reverse=reverse)
    elif by == "id":
        return sorted(books, key=lambda b: str(b.get("id", "")), reverse=reverse)
    else:
        return sorted(books, key=lambda b: b.get("title", "").lower(), reverse=reverse)


def add_book(
    books: List[Dict[str, Any]],
    book_id: str,
    title: str,
    author: str,
    category: str,
    year: int,
    total_copies: int = 1,
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Add a new book to the collection after validation."""
    clean_id = str(book_id).strip()
    clean_title = str(title).strip()
    clean_author = str(author).strip()
    clean_category = str(category).strip()

    is_valid, msg = validate_book_data(
        clean_id,
        clean_title,
        clean_author,
        clean_category,
        year,
        total_copies=total_copies,
        existing_books=books,
    )
    if not is_valid:
        return False, msg

    new_book = {
        "id": clean_id,
        "title": clean_title,
        "author": clean_author,
        "category": clean_category,
        "year": year,
        "total_copies": total_copies,
        "available_copies": total_copies,
        "available": True,
    }
    books.append(new_book)
    save_books(books, data_dir)
    return True, f"Book '{clean_title}' (ID: {clean_id}) added successfully with {total_copies} copy/copies."


def update_book(
    books: List[Dict[str, Any]],
    book_id: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    year: Optional[int] = None,
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Update existing book details."""
    book = find_book_by_id(book_id, books)
    if not book:
        return False, f"Book with ID '{book_id}' not found."

    new_title = title.strip() if title is not None else book["title"]
    new_author = author.strip() if author is not None else book["author"]
    new_category = category.strip() if category is not None else book["category"]
    new_year = year if year is not None else book["year"]

    is_valid, msg = validate_book_data(
        book["id"], new_title, new_author, new_category, new_year, existing_books=books, current_book_id=book["id"]
    )
    if not is_valid:
        return False, msg

    book["title"] = new_title
    book["author"] = new_author
    book["category"] = new_category
    book["year"] = new_year

    save_books(books, data_dir)
    return True, f"Book '{book['id']}' updated successfully."


def get_collection_statistics(books: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute and return collection metrics."""
    total = len(books)
    available_count = sum(1 for b in books if b.get("available"))
    borrowed_count = total - available_count

    categories: Dict[str, int] = {}
    years: List[int] = []

    for b in books:
        cat = b.get("category", "Uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
        yr = b.get("year")
        if isinstance(yr, int):
            years.append(yr)

    oldest_year = min(years) if years else None
    newest_year = max(years) if years else None

    return {
        "total_books": total,
        "available_books": available_count,
        "borrowed_books": borrowed_count,
        "categories": categories,
        "oldest_year": oldest_year,
        "newest_year": newest_year,
    }


def update_book_copies(
    books: List[Dict[str, Any]],
    book_id: str,
    new_total: int,
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Update total copies count for a book, adjusting available copies appropriately."""
    book = find_book_by_id(book_id, books)
    if not book:
        return False, f"Book with ID '{book_id}' not found."

    if new_total < 1:
        return False, "Total copies must be at least 1."

    old_total = int(book.get("total_copies", 1))
    current_avail = int(book.get("available_copies", old_total))
    borrowed_now = old_total - current_avail

    if new_total < borrowed_now:
        return (
            False,
            f"Cannot reduce total copies to {new_total}. Currently {borrowed_now} copies are borrowed out."
        )

    book["total_copies"] = new_total
    book["available_copies"] = new_total - borrowed_now
    book["available"] = book["available_copies"] > 0

    save_books(books, data_dir)
    return True, f"Copies for '{book['title']}' updated to {new_total} total ({book['available_copies']} available)."


def remove_book(
    books: List[Dict[str, Any]],
    book_id: str,
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Remove a book from the catalog if none of its copies are currently borrowed."""
    book = find_book_by_id(book_id, books)
    if not book:
        return False, f"Book with ID '{book_id}' not found."

    total = int(book.get("total_copies", 1))
    avail = int(book.get("available_copies", total))
    if avail < total:
        return False, f"Cannot remove '{book.get('title')}' because {total - avail} copy/copies are currently borrowed."

    books.remove(book)
    save_books(books, data_dir)
    return True, f"Book '{book.get('title')}' (ID: {book_id}) removed from catalog."


def render_books_table(books: List[Dict[str, Any]]) -> str:
    """Format a list of books into a clean ASCII table."""
    headers = ["ID", "Title", "Author", "Category", "Year", "Copies", "Status"]
    rows = []
    for b in books:
        total = b.get("total_copies", 1)
        avail = b.get("available_copies", 1 if b.get("available", True) else 0)
        status = get_book_status(b)
        rows.append([
            b.get("id", ""),
            b.get("title", ""),
            b.get("author", ""),
            b.get("category", ""),
            b.get("year", ""),
            f"{avail}/{total}",
            status,
        ])
    return utils.format_table(headers, rows, max_col_width=28)
