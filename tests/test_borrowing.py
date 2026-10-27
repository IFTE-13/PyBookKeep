"""Unit tests for borrowing.py module."""

import os
import shutil
import tempfile
import unittest

import books
import borrowing


class TestBorrowing(unittest.TestCase):
    """Test suite for borrowing transactions, return workflows, and limits."""

    def setUp(self) -> None:
        """Create an isolated temporary environment with initial books and empty records."""
        self.test_dir = tempfile.mkdtemp()
        self.test_books = [
            {"id": "B1", "title": "Book One", "author": "Author A", "category": "Cat", "year": 2020, "available": True},
            {"id": "B2", "title": "Book Two", "author": "Author B", "category": "Cat", "year": 2021, "available": True},
            {"id": "B3", "title": "Book Three", "author": "Author C", "category": "Cat", "year": 2022, "available": True},
            {"id": "B4", "title": "Book Four", "author": "Author D", "category": "Cat", "year": 2023, "available": True},
            {"id": "B5", "title": "Book Five", "author": "Author E", "category": "Cat", "year": 2024, "available": False},
        ]
        books.save_books(self.test_books, data_dir=self.test_dir)
        borrowing.save_borrowing_records([], data_dir=self.test_dir)

    def tearDown(self) -> None:
        """Clean up the test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_borrow_available_book_success(self) -> None:
        """Verify borrowing an available book succeeds and updates status."""
        current_books = books.load_books(data_dir=self.test_dir)
        records = borrowing.load_borrowing_records(data_dir=self.test_dir)

        success, msg = borrowing.borrow_book(
            "student1", "B1", current_books, records, data_dir=self.test_dir
        )
        self.assertTrue(success)
        self.assertIn("Success", msg)

        # Check book status in storage
        reloaded_books = books.load_books(data_dir=self.test_dir)
        b1 = books.find_book_by_id("B1", reloaded_books)
        self.assertFalse(b1["available"])

        # Check borrowing records
        reloaded_records = borrowing.load_borrowing_records(data_dir=self.test_dir)
        self.assertEqual(len(reloaded_records), 1)
        self.assertEqual(reloaded_records[0]["username"], "student1")
        self.assertEqual(reloaded_records[0]["book_id"], "B1")
        self.assertEqual(reloaded_records[0]["status"], "active")
        self.assertIsNotNone(reloaded_records[0]["borrow_date"])
        self.assertIsNone(reloaded_records[0]["return_date"])

    def test_borrow_already_unavailable_book_fails(self) -> None:
        """Verify attempting to borrow an already unavailable book is rejected."""
        current_books = books.load_books(data_dir=self.test_dir)
        records = borrowing.load_borrowing_records(data_dir=self.test_dir)

        success, msg = borrowing.borrow_book(
            "student1", "B5", current_books, records, data_dir=self.test_dir
        )
        self.assertFalse(success)
        self.assertIn("unavailable", msg.lower())

    def test_enforce_borrowing_limit(self) -> None:
        """Verify borrowing stops at the max limit (3 books)."""
        current_books = books.load_books(data_dir=self.test_dir)
        records = borrowing.load_borrowing_records(data_dir=self.test_dir)

        # Borrow 3 books
        borrowing.borrow_book("student1", "B1", current_books, records, data_dir=self.test_dir)
        borrowing.borrow_book("student1", "B2", current_books, records, data_dir=self.test_dir)
        borrowing.borrow_book("student1", "B3", current_books, records, data_dir=self.test_dir)

        # Try to borrow a 4th book
        success, msg = borrowing.borrow_book(
            "student1", "B4", current_books, records, data_dir=self.test_dir
        )
        self.assertFalse(success)
        self.assertIn("limit reached", msg.lower())

        # Verify B4 is still available
        reloaded_books = books.load_books(data_dir=self.test_dir)
        b4 = books.find_book_by_id("B4", reloaded_books)
        self.assertTrue(b4["available"])

    def test_return_book_success(self) -> None:
        """Verify returning a borrowed book resets availability and marks record returned."""
        current_books = books.load_books(data_dir=self.test_dir)
        records = borrowing.load_borrowing_records(data_dir=self.test_dir)

        # First borrow
        borrowing.borrow_book("student1", "B1", current_books, records, data_dir=self.test_dir)

        # Return book
        success, msg = borrowing.return_book(
            "student1", "B1", current_books, records, data_dir=self.test_dir
        )
        self.assertTrue(success)
        self.assertIn("returned", msg.lower())

        # Verify book is available again
        reloaded_books = books.load_books(data_dir=self.test_dir)
        b1 = books.find_book_by_id("B1", reloaded_books)
        self.assertTrue(b1["available"])

        # Verify record has return_date and status 'returned'
        reloaded_records = borrowing.load_borrowing_records(data_dir=self.test_dir)
        self.assertEqual(len(reloaded_records), 1)
        self.assertEqual(reloaded_records[0]["status"], "returned")
        self.assertIsNotNone(reloaded_records[0]["return_date"])

    def test_reject_unauthorized_return(self) -> None:
        """Verify returning a book the user hasn't borrowed fails."""
        current_books = books.load_books(data_dir=self.test_dir)
        records = borrowing.load_borrowing_records(data_dir=self.test_dir)

        # student1 borrows B1
        borrowing.borrow_book("student1", "B1", current_books, records, data_dir=self.test_dir)

        # student2 tries to return B1
        success, msg = borrowing.return_book(
            "student2", "B1", current_books, records, data_dir=self.test_dir
        )
        self.assertFalse(success)
        self.assertIn("No active borrowing record found", msg)

        # student1 tries to return B2 (which they never borrowed)
        success2, msg2 = borrowing.return_book(
            "student1", "B2", current_books, records, data_dir=self.test_dir
        )
        self.assertFalse(success2)


if __name__ == "__main__":
    unittest.main()
