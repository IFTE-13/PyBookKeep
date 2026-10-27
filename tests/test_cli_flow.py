"""Integration tests for Simple Library Management CLI operations."""

import io
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from main import SimpleLibraryCLI


class TestCLIFlow(unittest.TestCase):
    """End-to-end integration tests for simple admin CLI flows."""

    def setUp(self) -> None:
        """Create an isolated test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.app = SimpleLibraryCLI(data_dir=self.test_dir)

    def tearDown(self) -> None:
        """Clean up the test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_student_flow(self) -> None:
        """Test adding a student via CLI handler."""
        with patch("builtins.input", side_effect=["S999", "New Student", "Computer Science", "new@univ.edu", ""]):
            self.app.handle_add_student()

        # Check in memory and disk
        self.app.reload_data()
        student = next((s for s in self.app.students if s["id"] == "S999"), None)
        self.assertIsNotNone(student)
        self.assertEqual(student["name"], "New Student")

    def test_add_book_flow(self) -> None:
        """Test adding a book via CLI handler."""
        with patch("builtins.input", side_effect=["B999", "Modern Operating Systems", "Andrew Tanenbaum", "Computer Science", "2023", "2", ""]):
            self.app.handle_add_book()

        self.app.reload_data()
        book = next((b for b in self.app.books if b["id"] == "B999"), None)
        self.assertIsNotNone(book)
        self.assertEqual(book["total_copies"], 2)
        self.assertEqual(book["available_copies"], 2)

    def test_borrow_and_return_flow(self) -> None:
        """Test admin checkout and return flow."""
        # Book B101 starts with copies
        b101 = next(b for b in self.app.books if b["id"] == "B101")
        initial_avail = b101["available_copies"]

        # Admin borrows B101 to student S101
        with patch("builtins.input", side_effect=["B101", "S101", ""]):
            self.app.handle_borrow_book()

        self.app.reload_data()
        b101_after = next(b for b in self.app.books if b["id"] == "B101")
        self.assertEqual(b101_after["available_copies"], initial_avail - 1)

        # Check active borrowing record exists
        active_loans = [r for r in self.app.borrow_records if r.get("status") == "active"]
        self.assertTrue(len(active_loans) >= 1)
        rec_id = active_loans[0]["record_id"]

        # Admin returns the book using record ID option (1)
        with patch("builtins.input", side_effect=["1", rec_id, ""]):
            self.app.handle_return_book()

        self.app.reload_data()
        b101_returned = next(b for b in self.app.books if b["id"] == "B101")
        self.assertEqual(b101_returned["available_copies"], initial_avail)

    def test_search_books_flow(self) -> None:
        """Test search books flow in CLI."""
        with patch("builtins.input", side_effect=["1", "python", ""]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                self.app.handle_search_books()
                output = mock_stdout.getvalue()
                self.assertIn("Python", output)


if __name__ == "__main__":
    unittest.main()
