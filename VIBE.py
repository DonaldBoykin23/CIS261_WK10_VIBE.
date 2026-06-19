"""Student Grade Calculator

This program manages student records, calculates averages and letter grades,
and persists records in a pipe-delimited file.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import List

DATA_FILE = "student_grades.txt"


@dataclass
class Student:
    name: str
    student_id: str
    test_scores: List[float]
    average: float = field(init=False)
    grade: str = field(init=False)

    def __post_init__(self) -> None:
        self.update_scores(self.test_scores)

    def update_scores(self, scores: List[float]) -> None:
        self.test_scores = scores
        self.average = calculate_average(scores)
        self.grade = determine_letter_grade(self.average)

    def to_file_line(self) -> str:
        return (
            f"{self.name}|{self.student_id}|"
            f"{self.test_scores[0]:.2f}|{self.test_scores[1]:.2f}|{self.test_scores[2]:.2f}|"
            f"{self.average:.2f}|{self.grade}\n"
        )


def calculate_average(scores: List[float]) -> float:
    return sum(scores) / len(scores)


def determine_letter_grade(average: float) -> str:
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def load_students_from_file(filename: str) -> List[Student]:
    students: List[Student] = []
    if not os.path.exists(filename):
        return students

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) < 6:
                    print(f"Warning: invalid record on line {line_number}, skipping.")
                    continue

                name, student_id, *score_parts = parts
                try:
                    test_scores = [float(score_parts[i]) for i in range(3)]
                except (ValueError, IndexError):
                    print(f"Warning: invalid scores on line {line_number}, skipping.")
                    continue

                students.append(Student(name=name, student_id=student_id, test_scores=test_scores))
    except OSError as error:
        print(f"Error reading {filename}: {error}")

    return students


def save_students_to_file(filename: str, students: List[Student]) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for student in students:
                file.write(student.to_file_line())
        print(f"Records saved to {filename}.")
    except OSError as error:
        print(f"Error saving to {filename}: {error}")


def get_non_empty_input(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a non-empty value.")


def get_float_input(prompt: str, minimum: float = 0.0, maximum: float = 100.0) -> float:
    while True:
        value = input(prompt).strip()
        try:
            result = float(value)
            if result < minimum or result > maximum:
                raise ValueError
            return result
        except ValueError:
            print(f"Please enter a number between {minimum:.2f} and {maximum:.2f}.")


def add_new_student(students: List[Student]) -> None:
    print("\nAdd New Student")
    name = get_non_empty_input("Student name: ")
    student_id = get_non_empty_input("Student ID: ")
    scores = [
        get_float_input("Test 1 score (0-100): "),
        get_float_input("Test 2 score (0-100): "),
        get_float_input("Test 3 score (0-100): "),
    ]
    student = Student(name=name, student_id=student_id, test_scores=scores)
    students.append(student)
    print(
        f"Added {student.name} (ID: {student.student_id}) with average {student.average:.2f} "
        f"and grade {student.grade}."
    )


def display_students(students: List[Student]) -> None:
    if not students:
        print("No students available to display.")
        return

    print("\nStudent Records")
    print("-" * 78)
    print(
        f"{'Name':<20} {'ID':<12} {'Test 1':>7} {'Test 2':>7} {'Test 3':>7} "
        f"{'Average':>8} {'Grade':>7}"
    )
    print("-" * 78)
    for student in students:
        print(
            f"{student.name:<20} {student.student_id:<12} "
            f"{student.test_scores[0]:>7.2f} {student.test_scores[1]:>7.2f} "
            f"{student.test_scores[2]:>7.2f} {student.average:>8.2f} {student.grade:>7}"
        )
    print("-" * 78)


def calculate_class_statistics(students: List[Student]) -> tuple[float, float, float]:
    averages = [student.average for student in students]
    highest = max(averages)
    lowest = min(averages)
    class_average = sum(averages) / len(averages)
    return highest, lowest, class_average


def display_statistics(students: List[Student]) -> None:
    if not students:
        print("No student records available to calculate statistics.")
        return

    highest, lowest, class_average = calculate_class_statistics(students)
    print("\nClass Statistics")
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average : {lowest:.2f}")
    print(f"Class average  : {class_average:.2f}")


def search_student_by_name(students: List[Student]) -> None:
    if not students:
        print("No students available to search.")
        return

    query = get_non_empty_input("Enter student name to search: ").lower()
    matches = [student for student in students if query in student.name.lower()]

    if not matches:
        print(f"No student found matching '{query}'.")
        return

    print(f"\nFound {len(matches)} student(s) matching '{query}':")
    print("-" * 78)
    print(
        f"{'Name':<20} {'ID':<12} {'Test 1':>7} {'Test 2':>7} {'Test 3':>7} "
        f"{'Average':>8} {'Grade':>7}"
    )
    print("-" * 78)
    for student in matches:
        print(
            f"{student.name:<20} {student.student_id:<12} "
            f"{student.test_scores[0]:>7.2f} {student.test_scores[1]:>7.2f} "
            f"{student.test_scores[2]:>7.2f} {student.average:>8.2f} {student.grade:>7}"
        )
    print("-" * 78)


def read_single_key() -> str:
    try:
        import msvcrt

        return msvcrt.getwch()
    except ImportError:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
            return char
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_menu_selection() -> str:
    print("\nMenu")
    print("1. Add new student record")
    print("2. Display all student records")
    print("3. Search for a student by name")
    print("4. Display class statistics")
    print("5. Save records now")
    print("Press ESC to exit.")
    print("Enter a menu number or press ESC:", end=" ", flush=True)

    choice = read_single_key()
    if choice == "\x1b":
        print()
        return "ESC"

    print(choice)
    return choice


def main() -> None:
    students = load_students_from_file(DATA_FILE)
    if students:
        print(f"Loaded {len(students)} student record(s) from {DATA_FILE}.")
    else:
        print("No existing records found. Starting with an empty class list.")

    while True:
        selection = get_menu_selection()
        if selection == "1":
            add_new_student(students)
        elif selection == "2":
            display_students(students)
        elif selection == "3":
            search_student_by_name(students)
        elif selection == "4":
            display_statistics(students)
        elif selection == "5":
            save_students_to_file(DATA_FILE, students)
        elif selection.upper() == "ESC":
            print("\nExiting program.")
            save_students_to_file(DATA_FILE, students)
            break
        else:
            print("Please select a valid option from the menu.")

    print("Goodbye!")


if __name__ == "__main__":
    main()
