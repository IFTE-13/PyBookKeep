"""Unit tests for books.py module."""

import os
import shutil
import tempfile
import unittest

import books


class TestBooks(unittest.TestCase):
    """Test suite for book catalog operations, search, sort, and validation."""

    def setUp(self) -> None:
        """Create an isolated temporary environment with initial test books."""
        self.test_dir = tempfile.mkdtemp()
        self.sample_books = [
            {
                "id": "T1",
                "title": "Python Basics",
                "author": "Alice Smith",
                "category": "Education",
                "year": 2021,
                "available": True,
            },
            {
                "id": "T2",
                "title": "Advanced Python Tricks",
                "author": "Bob Jones",
                "category": "Programming",
                "year": 2023,
                "available": False,
            },
            {
                "id": "T3",
                "title": "Data Structures in C",
                "author": "Carol White",
                "category": "Computer Science",
                "year": 2019,
                "available": True,
            },
        ]
        books.save_books(self.sample_books, data_dir=self.test_dir)

    def tearDown(self) -> None:
        """Clean up the test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_valid_book(self) -> None:
        """Verify adding a completely valid book succeeds."""
        current_books = books.load_books(data_dir=self.test_dir)
        success, msg = books.add_book(
            current_books,
            book_id="T4",
            title="Clean Architecture",
            author="Robert Martin",
            category="Software Engineering",
            year=2017,
            data_dir=self.test_dir,
        )
        self.assertTrue(success)
        self.assertIn("added successfully", msg)

        # Verify saved in storage
        reloaded = books.load_books(data_dir=self.test_dir)
        self.assertEqual(len(reloaded), 4)
        found = books.find_book_by_id("T4", reloaded)
        self.assertIsNotNone(found)
        self.assertEqual(found["title"], "Clean Architecture")

    def test_reject_duplicate_book_id(self) -> None:
        """Verify adding a book with an existing ID fails."""
        current_books = books.load_books(data_dir=self.test_dir)
        success, msg = books.add_book(
            current_books,
            book_id="T1",  # Already exists
            title="Duplicate Book",
            author="Someone",
            category="General",
            year=2020,
            data_dir=self.test_dir,
        )
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_reject_invalid_year(self) -> None:
        """Verify adding a book with invalid publication year fails."""
        current_books = books.load_books(data_dir=self.test_dir)
        # Year in future
        success, msg = books.add_book(
            current_books, "T99", "Future Book", "Author", "Fiction", 3050, data_dir=self.test_dir
        )
        self.assertFalse(success)
        self.assertIn("Publication year", msg)

        # Year negative
        success2, msg2 = books.add_book(
            current_books, "T98", "Ancient Book", "Author", "History", -50, data_dir=self.test_dir
        )
        self.assertFalse(success2)

    def test_reject_empty_required_fields(self) -> None:
        """Verify adding a book with empty title/author/category fails."""
        current_books = books.load_books(data_dir=self.test_dir)
        success, msg = books.add_book(
            current_books, "T97", "   ", "Author", "Category", 2020, data_dir=self.test_dir
        )
        self.assertFalse(success)
        self.assertIn("Title cannot be empty", msg)

    def test_search_books(self) -> None:
        """Verify case-insensitive search by title, author, category, and all fields."""
        current_books = books.load_books(data_dir=self.test_dir)

        # By title substring
        res_title = books.search_books(current_books, "python", field="title")
        self.assertEqual(len(res_title), 2)

        # By author
        res_author = books.search_books(current_books, "white", field="author")
        self.assertEqual(len(res_author), 1)
        self.assertEqual(res_author[0]["id"], "T3")

        # By category
        res_cat = books.search_books(current_books, "science", field="category")
        self.assertEqual(len(res_cat), 1)

        # Across all fields
        res_all = books.search_books(current_books, "jones", field="all")
        self.assertEqual(len(res_all), 1)
        self.assertEqual(res_all[0]["id"], "T2")

    def test_filter_books_by_availability(self) -> None:
        """Verify filtering for available vs borrowed books."""
        current_books = books.load_books(data_dir=self.test_dir)

        available_books = books.filter_books_by_availability(current_books, available_only=True)
        self.assertEqual(len(available_books), 2)
        for b in available_books:
            self.assertTrue(b["available"])

        borrowed_books = books.filter_books_by_availability(current_books, available_only=False)
        self.assertEqual(len(borrowed_books), 1)
        self.assertEqual(borrowed_books[0]["id"], "T2")

    def test_sort_books(self) -> None:
        """Verify sorting by title and publication year."""
        current_books = books.load_books(data_dir=self.test_dir)

        sorted_by_year_asc = books.sort_books(current_books, by="year", reverse=False)
        self.assertEqual([b["id"] for b in sorted_by_year_asc], ["T3", "T1", "T2"])

        sorted_by_title_desc = books.sort_books(current_books, by="title", reverse=True)
        self.assertEqual(sorted_by_title_desc[0]["id"], "T1")  # "Python Basics"

    def test_update_book(self) -> None:
        """Verify updating existing book fields."""
        current_books = books.load_books(data_dir=self.test_dir)
        success, msg = books.update_book(
            current_books,
            book_id="T1",
            title="Python Basics 2nd Edition",
            year=2024,
            data_dir=self.test_dir,
        )
        self.assertTrue(success)

        reloaded = books.load_books(data_dir=self.test_dir)
        t1 = books.find_book_by_id("T1", reloaded)
        self.assertEqual(t1["title"], "Python Basics 2nd Edition")
        self.assertEqual(t1["year"], 2024)

    def test_remove_book(self) -> None:
        """Verify removing available book succeeds, but borrowed book fails."""
        current_books = books.load_books(data_dir=self.test_dir)

        # Try to remove borrowed book (T2) -> should fail
        fail_res, fail_msg = books.remove_book(current_books, "T2", data_dir=self.test_dir)
        self.assertFalse(fail_res)
        self.assertIn("currently borrowed", fail_msg)

        # Remove available book (T3) -> should succeed
        ok_res, ok_msg = books.remove_book(current_books, "T3", data_dir=self.test_dir)
        self.assertTrue(ok_res)
        self.assertIsNone(books.find_book_by_id("T3", current_books))

    def test_collection_statistics(self) -> None:
        """Verify statistics computation."""
        current_books = books.load_books(data_dir=self.test_dir)
        stats = books.get_collection_statistics(current_books)

        self.assertEqual(stats["total_books"], 3)
        self.assertEqual(stats["available_books"], 2)
        self.assertEqual(stats["borrowed_books"], 1)
        self.assertEqual(stats["oldest_year"], 2019)
        self.assertEqual(stats["newest_year"], 2023)
        self.assertIn("Education", stats["categories"])


if __name__ == "__main__":
    unittest.main()
