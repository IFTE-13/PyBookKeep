"""Unit tests for storage.py module."""

import json
import os
import shutil
import tempfile
import unittest

import storage


class TestStorage(unittest.TestCase):
    """Test suite for JSON persistence and error handling."""

    def setUp(self) -> None:
        """Create an isolated temporary directory for test storage."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """Remove the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_json_success(self) -> None:
        """Verify normal data persistence and retrieval."""
        file_path = os.path.join(self.test_dir, "test.json")
        sample_data = [{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]

        storage.save_json(file_path, sample_data)
        loaded = storage.load_json(file_path)

        self.assertEqual(loaded, sample_data)

    def test_load_non_existent_file_returns_default(self) -> None:
        """Verify that loading a non-existent file returns the specified default."""
        file_path = os.path.join(self.test_dir, "missing.json")
        result = storage.load_json(file_path, default_data=["fallback"])
        self.assertEqual(result, ["fallback"])

    def test_load_empty_file_returns_default(self) -> None:
        """Verify that an empty file safely returns default data instead of failing."""
        file_path = os.path.join(self.test_dir, "empty.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("   \n")

        result = storage.load_json(file_path, default_data={"key": "val"})
        self.assertEqual(result, {"key": "val"})

    def test_load_malformed_json_raises_error_without_wiping(self) -> None:
        """Verify that malformed JSON raises ValueError and preserves file content."""
        file_path = os.path.join(self.test_dir, "corrupted.json")
        corrupted_content = "{ this is invalid json !!!"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(corrupted_content)

        with self.assertRaises(ValueError) as ctx:
            storage.load_json(file_path)

        self.assertIn("Failed to decode JSON", str(ctx.exception))

        # Check file content was not wiped
        with open(file_path, "r", encoding="utf-8") as f:
            still_intact = f.read()
        self.assertEqual(still_intact, corrupted_content)

    def test_initialize_file_if_missing(self) -> None:
        """Verify initialize_file_if_missing only writes when file does not exist."""
        file_path = os.path.join(self.test_dir, "init.json")
        initial_data = ["default"]

        # First time: should create file and return True
        created = storage.initialize_file_if_missing(file_path, initial_data)
        self.assertTrue(created)
        self.assertEqual(storage.load_json(file_path), initial_data)

        # Second time: should not overwrite existing file and return False
        modified_data = ["modified"]
        storage.save_json(file_path, modified_data)
        second_call = storage.initialize_file_if_missing(file_path, initial_data)
        self.assertFalse(second_call)
        self.assertEqual(storage.load_json(file_path), modified_data)


if __name__ == "__main__":
    unittest.main()
