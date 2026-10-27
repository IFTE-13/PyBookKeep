# PyBookKeep — Simple Library Management System

A lightweight, terminal-based Library Management System built with Python. Designed for single-administrator use with zero setup, zero complex authentication, and zero unnecessary extras.

---

## Features

- **No Authentication / Direct Admin Access**: Launches directly into the administrator console.
- **Book Inventory & Copy Tracking**: Manage books with total copies and available copies. Real-time availability status displays either `Available (X/Y)` or `All copies given away`.
- **Student Directory**: Store student records with Student ID, Full Name, Department, and Contact Info.
- **Borrowing & Return Lifecycle**:
  - Automatically checks stock before loaning a book copy.
  - Generates unique borrow record IDs (e.g. `REC-0001`).
  - Logs exact return timestamps upon return and restores available copies.
- **Complete Borrow History**: Easily view active loans or filter full historical records across students.
- **Safe JSON Storage**: Atomic file writing prevents data corruption on unexpected interruptions.

---

## Menu Options & What They Do

When you run the system, you are greeted with the main menu:

```text
========================================================================
                    SIMPLE LIBRARY MANAGEMENT SYSTEM
                         (Administrator Console)
========================================================================

  1. Manage Books (Catalog & Copy Stock)
  2. Manage Students (Records & Directory)
  3. Borrow Book (Checkout to Student)
  4. Return Book (Checkin & Return Timestamp)
  5. View Borrow History & Active Loans
  0. Exit System
```

### 1. Manage Books
* **View All Books**: Displays a formatted ASCII table showing Book ID, Title, Author, Category, Publication Year, Copies (`Available/Total`), and Status (`Available (X/Y)` or `All copies given away`).
* **Search Books**: Search the catalog by title, author, category, or across all fields simultaneously.
* **Add New Book**: Registers a new book into the catalog with customizable initial copies.
* **Update Book Total Copies**: Adjust the total inventory count for any title (safeguarded against dropping below the number of currently borrowed copies).
* **Remove a Book**: Deletes a book from the catalog (allowed only if no copies are currently checked out).

### 2. Manage Students
* **View All Students**: Displays all registered students with their ID, Full Name, Department, and Contact details.
* **Search Students**: Search student records by Student ID, Name, or Department keyword.
* **Add New Student**: Registers a new student into the database with duplicate ID validation.

### 3. Borrow Book
* Displays currently available books.
* Prompts for **Book ID** and **Student ID**.
* Checks availability: if all copies are already borrowed, the loan is blocked with an informative message.
* On success, decrements available copy count, creates a loan record with the current timestamp, and outputs the confirmation with the new Record ID.

### 4. Return Book
* Shows all currently active loans.
* Allows returning through two flexible methods:
  1. **By Record ID** (e.g., `REC-0001`).
  2. **By Student ID and Book ID**.
* Records the return timestamp, marks record status as `Returned`, and increments the book's available copies back to inventory.

### 5. View Borrow History & Active Loans
* **View Currently Active Loans**: Quick filter showing only books currently out with students.
* **View Full Borrow History**: Chronological log of all checkouts and returns.
* **Filter by Student ID**: View complete borrowing history for a specific student.

---

## Project Structure

```text
PP/
├── books.py             # Book catalog management & copy inventory logic
├── students.py          # Student records and directory operations
├── borrowing.py         # Checkout, return workflows & history tracking
├── storage.py           # Atomic JSON read/write persistence
├── utils.py             # ASCII table formatter, terminal helpers & validators
├── main.py              # Main CLI entry point and menu router
├── tests/               # Comprehensive unit and integration test suite
│   ├── test_books.py
│   ├── test_borrowing.py
│   ├── test_cli_flow.py
│   ├── test_storage.py
│   └── test_students.py
└── data/                # Persistent JSON data files
    ├── books.json
    ├── students.json
    └── borrowing_records.json
```

---

## Getting Started

### Prerequisites
- Python 3.8+ (No external third-party dependencies required; uses standard library).

### Running the System
```bash
python main.py
```

### Running Tests
To run the automated test suite (29 tests):
```bash
python -m unittest discover tests
```
