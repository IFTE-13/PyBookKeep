"""Student management module for Simple Library Management System.

Handles storing, searching, validating, and displaying student records.
"""

from typing import Any, Dict, List, Optional, Tuple

import storage
import utils

STUDENTS_FILE = "students.json"


def get_default_students() -> List[Dict[str, Any]]:
    """Return default student records for initial setup."""
    return [
        {
            "id": "S101",
            "name": "Alex Johnson",
            "department": "Computer Science",
            "contact": "alex.j@university.edu",
        },
        {
            "id": "S102",
            "name": "Brianna Smith",
            "department": "Electrical Engineering",
            "contact": "brianna.s@university.edu",
        },
        {
            "id": "S103",
            "name": "Carlos Rivera",
            "department": "Information Technology",
            "contact": "carlos.r@university.edu",
        },
    ]


def load_students(data_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load students from storage. Initializes default students if missing."""
    file_path = storage.get_data_path(STUDENTS_FILE, data_dir)
    storage.initialize_file_if_missing(file_path, get_default_students())
    return storage.load_json(file_path, default_data=[])


def save_students(students: List[Dict[str, Any]], data_dir: Optional[str] = None) -> None:
    """Save students list to storage."""
    file_path = storage.get_data_path(STUDENTS_FILE, data_dir)
    storage.save_json(file_path, students)


def find_student_by_id(
    student_id: str, students: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Find and return a student by their ID, case-insensitively."""
    target = str(student_id).strip().lower()
    for student in students:
        if str(student.get("id", "")).strip().lower() == target:
            return student
    return None


def search_students(query: str, students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Search students by matching ID, name, department, or contact."""
    q = str(query).strip().lower()
    if not q:
        return list(students)

    results: List[Dict[str, Any]] = []
    for student in students:
        s_id = str(student.get("id", "")).lower()
        s_name = str(student.get("name", "")).lower()
        s_dept = str(student.get("department", "")).lower()
        s_contact = str(student.get("contact", "")).lower()

        if q in s_id or q in s_name or q in s_dept or q in s_contact:
            results.append(student)
    return results


def add_student(
    student_id: str,
    name: str,
    department: str,
    contact: str,
    students: List[Dict[str, Any]],
    data_dir: Optional[str] = None,
) -> Tuple[bool, str]:
    """Validate and add a new student record."""
    s_id = str(student_id).strip()
    s_name = str(name).strip()
    s_dept = str(department).strip()
    s_contact = str(contact).strip()

    if not s_id:
        return False, "Student ID cannot be empty."

    if find_student_by_id(s_id, students) is not None:
        return False, f"A student with ID '{s_id}' already exists."

    if not s_name:
        return False, "Student name cannot be empty."

    new_student = {
        "id": s_id,
        "name": s_name,
        "department": s_dept or "General",
        "contact": s_contact or "N/A",
    }
    students.append(new_student)
    save_students(students, data_dir)
    return True, f"Student '{s_name}' (ID: {s_id}) added successfully."


def format_students_table(students: List[Dict[str, Any]]) -> str:
    """Format a list of students into a readable text table."""
    headers = ["Student ID", "Full Name", "Department", "Contact"]
    rows = []
    for s in students:
        rows.append([
            s.get("id", "N/A"),
            s.get("name", "N/A"),
            s.get("department", "N/A"),
            s.get("contact", "N/A"),
        ])
    return utils.format_table(headers, rows)
