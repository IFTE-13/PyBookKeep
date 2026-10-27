"""Unit tests for students.py module."""

import os
import shutil
import tempfile
import unittest

import students


class TestStudents(unittest.TestCase):
    """Test suite for student registration, search, and validation."""

    def setUp(self) -> None:
        """Create an isolated temporary environment with initial test students."""
        self.test_dir = tempfile.mkdtemp()
        self.sample_students = [
            {
                "id": "S1",
                "name": "Alice Smith",
                "department": "Computer Science",
                "contact": "alice@univ.edu",
            },
            {
                "id": "S2",
                "name": "Bob Jones",
                "department": "Electrical Engineering",
                "contact": "bob@univ.edu",
            },
        ]
        students.save_students(self.sample_students, data_dir=self.test_dir)

    def tearDown(self) -> None:
        """Clean up the test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_and_save_students(self) -> None:
        """Verify saving and loading students persists data."""
        loaded = students.load_students(data_dir=self.test_dir)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["id"], "S1")

    def test_find_student_by_id(self) -> None:
        """Verify finding student by ID case-insensitively."""
        loaded = students.load_students(data_dir=self.test_dir)
        found = students.find_student_by_id("s1", loaded)
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Alice Smith")

        not_found = students.find_student_by_id("NONEXISTENT", loaded)
        self.assertIsNone(not_found)

    def test_add_student_success(self) -> None:
        """Verify adding a new student succeeds."""
        loaded = students.load_students(data_dir=self.test_dir)
        success, msg = students.add_student(
            student_id="S3",
            name="Charlie Davis",
            department="Mathematics",
            contact="charlie@univ.edu",
            students=loaded,
            data_dir=self.test_dir,
        )
        self.assertTrue(success)
        self.assertIn("added successfully", msg)

        # Verify in storage
        reloaded = students.load_students(data_dir=self.test_dir)
        self.assertEqual(len(reloaded), 3)

    def test_add_duplicate_student_id_fails(self) -> None:
        """Verify duplicate student ID is rejected."""
        loaded = students.load_students(data_dir=self.test_dir)
        success, msg = students.add_student(
            student_id="S1",
            name="Duplicate Alice",
            department="Physics",
            contact="dup@univ.edu",
            students=loaded,
            data_dir=self.test_dir,
        )
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_search_students(self) -> None:
        """Verify searching students by keyword in name or department."""
        loaded = students.load_students(data_dir=self.test_dir)
        matches = students.search_students("alice", loaded)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], "S1")

        dept_matches = students.search_students("Electrical", loaded)
        self.assertEqual(len(dept_matches), 1)
        self.assertEqual(dept_matches[0]["id"], "S2")


if __name__ == "__main__":
    unittest.main()
