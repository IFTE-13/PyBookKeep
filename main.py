"""Main entry point for Simple Library Management System.

A clean, single-admin Command-Line Library Management System to manage
books, students, copy availability, and borrowing/return history.
No authentication, no games, no quizzes.
"""

import sys
from typing import Any, Dict, List, Optional

import books as books_mod
import borrowing
import storage
import students as students_mod
import utils


class SimpleLibraryCLI:
    """Manages the Admin CLI state and operations."""

    def __init__(self, data_dir: Optional[str] = None) -> None:
        self.data_dir = data_dir
        self.books = books_mod.load_books(self.data_dir)
        self.students = students_mod.load_students(self.data_dir)
        self.borrow_records = borrowing.load_borrowing_records(self.data_dir)

    def reload_data(self) -> None:
        """Refresh in-memory state from disk."""
        self.books = books_mod.load_books(self.data_dir)
        self.students = students_mod.load_students(self.data_dir)
        self.borrow_records = borrowing.load_borrowing_records(self.data_dir)

    # ------------------------------------------------------------------
    # Book Management
    # ------------------------------------------------------------------
    def menu_manage_books(self) -> None:
        """Book management submenu."""
        while True:
            utils.print_banner("Book Management", "Manage catalog and copy stock")
            print("  1. View All Books")
            print("  2. Search Books")
            print("  3. Add New Book")
            print("  4. Update Book Total Copies")
            print("  5. Remove a Book")
            print("  0. Back to Main Menu")

            choice = utils.get_non_empty_input("\nEnter choice [0-5]: ")
            if choice in ("0", None):
                break
            elif choice == "1":
                self.handle_view_books()
            elif choice == "2":
                self.handle_search_books()
            elif choice == "3":
                self.handle_add_book()
            elif choice == "4":
                self.handle_update_copies()
            elif choice == "5":
                self.handle_remove_book()
            else:
                utils.print_error("Invalid selection. Please choose an option from the menu.")
                utils.pause()

    def handle_view_books(self) -> None:
        """Display all books with copy count and status."""
        utils.print_header("Book Catalog")
        if not self.books:
            print("  Catalog is empty.")
        else:
            print(books_mod.render_books_table(self.books))
            total_titles = len(self.books)
            total_copies = sum(int(b.get("total_copies", 1)) for b in self.books)
            avail_copies = sum(int(b.get("available_copies", 0)) for b in self.books)
            print(f"\n  Total Titles: {total_titles} | Total Copies: {total_copies} | Available Copies: {avail_copies}")
        utils.pause()

    def handle_search_books(self) -> None:
        """Search books by title, author, or category."""
        utils.print_header("Search Books")
        print("  1. By Title")
        print("  2. By Author")
        print("  3. By Category")
        print("  4. All Fields")
        print("  0. Cancel")

        choice = utils.get_non_empty_input("\nChoose search field: ")
        field_map = {"1": "title", "2": "author", "3": "category", "4": "all"}
        if choice not in field_map:
            return

        query = utils.get_non_empty_input("Enter search keyword: ")
        if not query:
            return

        matches = books_mod.search_books(self.books, query, field=field_map[choice])
        print(f"\nFound {len(matches)} matching book(s):")
        print(books_mod.render_books_table(matches))
        utils.pause()

    def handle_add_book(self) -> None:
        """Prompt admin to register a new book."""
        utils.print_header("Add New Book to Catalog")
        print("  (Type 'cancel' at any prompt to abort)")

        book_id = utils.get_non_empty_input("Book ID (e.g. B109): ")
        if not book_id:
            return

        title = utils.get_non_empty_input("Title: ")
        if not title:
            return

        author = utils.get_non_empty_input("Author: ")
        if not author:
            return

        category = utils.get_non_empty_input("Category: ")
        if not category:
            return

        year = utils.get_int_input("Publication Year (e.g. 2024): ", min_val=1000, max_val=2100)
        if year is None:
            return

        total_copies = utils.get_int_input("Number of Copies (default 1): ", min_val=1, max_val=1000)
        if total_copies is None:
            total_copies = 1

        success, message = books_mod.add_book(
            books=self.books,
            book_id=book_id,
            title=title,
            author=author,
            category=category,
            year=year,
            total_copies=total_copies,
            data_dir=self.data_dir,
        )
        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    def handle_update_copies(self) -> None:
        """Update the total stock of copies for a book."""
        utils.print_header("Update Book Total Copies")
        print(books_mod.render_books_table(self.books))

        book_id = utils.get_non_empty_input("\nEnter Book ID to update: ")
        if not book_id:
            return

        book = books_mod.find_book_by_id(book_id, self.books)
        if not book:
            utils.print_error(f"Book with ID '{book_id}' not found.")
            utils.pause()
            return

        print(f"\nSelected: '{book['title']}' | Current Total Copies: {book.get('total_copies', 1)} | Available: {book.get('available_copies', 0)}")
        new_total = utils.get_int_input("Enter new total copies: ", min_val=1)
        if new_total is None:
            return

        success, message = books_mod.update_book_copies(
            books=self.books,
            book_id=book["id"],
            new_total=new_total,
            data_dir=self.data_dir,
        )
        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    def handle_remove_book(self) -> None:
        """Remove a book from catalog if no copies are borrowed."""
        utils.print_header("Remove Book")
        book_id = utils.get_non_empty_input("Enter Book ID to remove: ")
        if not book_id:
            return

        if not utils.get_confirmation(f"Are you sure you want to remove book '{book_id}'?", default_yes=False):
            print("Operation cancelled.")
            utils.pause()
            return

        success, message = books_mod.remove_book(self.books, book_id, self.data_dir)
        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    # ------------------------------------------------------------------
    # Student Management
    # ------------------------------------------------------------------
    def menu_manage_students(self) -> None:
        """Student management submenu."""
        while True:
            utils.print_banner("Student Management", "Register and search students")
            print("  1. View All Students")
            print("  2. Search Students")
            print("  3. Add New Student")
            print("  0. Back to Main Menu")

            choice = utils.get_non_empty_input("\nEnter choice [0-3]: ")
            if choice in ("0", None):
                break
            elif choice == "1":
                self.handle_view_students()
            elif choice == "2":
                self.handle_search_students()
            elif choice == "3":
                self.handle_add_student()
            else:
                utils.print_error("Invalid selection.")
                utils.pause()

    def handle_view_students(self) -> None:
        """Display all students."""
        utils.print_header("Registered Students")
        if not self.students:
            print("  No students registered yet.")
        else:
            print(students_mod.format_students_table(self.students))
            print(f"\n  Total Registered Students: {len(self.students)}")
        utils.pause()

    def handle_search_students(self) -> None:
        """Search student records."""
        utils.print_header("Search Students")
        query = utils.get_non_empty_input("Enter Student ID, Name, or Department: ")
        if not query:
            return

        matches = students_mod.search_students(query, self.students)
        print(f"\nFound {len(matches)} matching student(s):")
        print(students_mod.format_students_table(matches))
        utils.pause()

    def handle_add_student(self) -> None:
        """Register a new student."""
        utils.print_header("Add New Student")
        student_id = utils.get_non_empty_input("Student ID (e.g. S104): ")
        if not student_id:
            return

        name = utils.get_non_empty_input("Full Name: ")
        if not name:
            return

        department = utils.get_non_empty_input("Department (e.g. Computer Science): ")
        if not department:
            return

        contact = utils.get_non_empty_input("Contact Email / Phone: ")
        if not contact:
            return

        success, message = students_mod.add_student(
            student_id=student_id,
            name=name,
            department=department,
            contact=contact,
            students=self.students,
            data_dir=self.data_dir,
        )
        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    # ------------------------------------------------------------------
    # Borrow & Return Workflows
    # ------------------------------------------------------------------
    def handle_borrow_book(self) -> None:
        """Admin checkout flow: assign a book copy to a student."""
        utils.print_banner("Borrow Book", "Checkout a book copy to a student")

        # Show catalog
        print(books_mod.render_books_table(self.books))

        book_id = utils.get_non_empty_input("\nEnter Book ID to borrow (or 'cancel'): ")
        if not book_id:
            return

        book = books_mod.find_book_by_id(book_id, self.books)
        if not book:
            utils.print_error(f"Book with ID '{book_id}' does not exist.")
            utils.pause()
            return

        avail = int(book.get("available_copies", 0))
        if avail <= 0:
            utils.print_error(f"Cannot borrow: All copies of '{book['title']}' are currently given away!")
            utils.pause()
            return

        print(f"\nSelected Book: {book['title']} (Available: {avail}/{book.get('total_copies', 1)})")
        print("\nRegistered Students:")
        print(students_mod.format_students_table(self.students))

        student_id = utils.get_non_empty_input("\nEnter Student ID borrowing this book: ")
        if not student_id:
            return

        student = students_mod.find_student_by_id(student_id, self.students)
        if not student:
            utils.print_error(f"Student '{student_id}' not found.")
            utils.pause()
            return

        success, message = borrowing.borrow_book(
            student_id=student["id"],
            book_id=book["id"],
            books=self.books,
            students=self.students,
            records=self.borrow_records,
            data_dir=self.data_dir,
        )
        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    def handle_return_book(self) -> None:
        """Admin return flow: check in a previously borrowed book."""
        utils.print_banner("Return Book", "Process return and restore book copy")

        active_loans = borrowing.get_active_borrowings(self.borrow_records)
        if not active_loans:
            print("  There are currently no active book loans. All copies are returned!")
            utils.pause()
            return

        print("Currently Active Loans:")
        print(borrowing.render_borrowings_table(active_loans, active_only=True))

        print("\nOptions:")
        print("  1. Return by Record ID (e.g. REC-0001)")
        print("  2. Return by Student ID and Book ID")
        print("  0. Cancel")

        choice = utils.get_non_empty_input("\nChoose option: ")
        if choice in ("0", None):
            return
        elif choice == "1":
            record_id = utils.get_non_empty_input("Enter Record ID to return: ")
            if not record_id:
                return
            success, message = borrowing.return_book_by_record(
                record_id=record_id,
                books=self.books,
                records=self.borrow_records,
                data_dir=self.data_dir,
            )
        elif choice == "2":
            student_id = utils.get_non_empty_input("Enter Student ID: ")
            if not student_id:
                return
            book_id = utils.get_non_empty_input("Enter Book ID: ")
            if not book_id:
                return
            success, message = borrowing.return_book(
                student_id=student_id,
                book_id=book_id,
                books=self.books,
                records=self.borrow_records,
                data_dir=self.data_dir,
            )
        else:
            utils.print_error("Invalid option.")
            utils.pause()
            return

        if success:
            utils.print_success(message)
        else:
            utils.print_error(message)
        utils.pause()

    def handle_borrow_history(self) -> None:
        """View borrowing history and filter active loans."""
        while True:
            utils.print_banner("Borrow History", "View active loans and return records")
            print("  1. View Currently Active Loans")
            print("  2. View Full Borrow History (All time)")
            print("  3. View Borrow History for a Specific Student")
            print("  0. Back to Main Menu")

            choice = utils.get_non_empty_input("\nEnter choice [0-3]: ")
            if choice in ("0", None):
                break
            elif choice == "1":
                active = borrowing.get_active_borrowings(self.borrow_records)
                utils.print_header(f"Active Loans ({len(active)} active)")
                if not active:
                    print("  No active loans.")
                else:
                    print(borrowing.render_borrowings_table(active, active_only=True))
                utils.pause()
            elif choice == "2":
                history = borrowing.get_borrow_history(self.borrow_records)
                utils.print_header(f"Full Borrow History ({len(history)} total records)")
                if not history:
                    print("  No borrow records found.")
                else:
                    print(borrowing.render_borrowings_table(history, active_only=False))
                utils.pause()
            elif choice == "3":
                student_id = utils.get_non_empty_input("Enter Student ID: ")
                if not student_id:
                    continue
                records = borrowing.get_borrowings_for_student(student_id, self.borrow_records)
                utils.print_header(f"Records for Student '{student_id}' ({len(records)} found)")
                if not records:
                    print(f"  No records found for student '{student_id}'.")
                else:
                    print(borrowing.render_borrowings_table(records, active_only=False))
                utils.pause()
            else:
                utils.print_error("Invalid selection.")
                utils.pause()

    # ------------------------------------------------------------------
    # Main Event Loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Main execution loop for the admin console."""
        while True:
            utils.print_banner(
                "Simple Library Management System",
                "Administrator Console",
            )
            print("  1. Manage Books (Catalog & Copy Stock)")
            print("  2. Manage Students (Records & Directory)")
            print("  3. Borrow Book (Checkout to Student)")
            print("  4. Return Book (Checkin & Return Timestamp)")
            print("  5. View Borrow History & Active Loans")
            print("  0. Exit System")

            choice = utils.get_non_empty_input("\nEnter selection [0-5]: ")
            if choice in ("0", "exit", "quit"):
                print("\nExiting Library Management System. Goodbye!\n")
                break
            elif choice == "1":
                self.menu_manage_books()
            elif choice == "2":
                self.menu_manage_students()
            elif choice == "3":
                self.handle_borrow_book()
            elif choice == "4":
                self.handle_return_book()
            elif choice == "5":
                self.handle_borrow_history()
            else:
                utils.print_error("Invalid option. Please enter a number from 0 to 5.")
                utils.pause()


def main() -> None:
    """Entry point."""
    app = SimpleLibraryCLI()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted. Exiting system.")
        sys.exit(0)


if __name__ == "__main__":
    main()
