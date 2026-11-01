from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_FILE = Path(__file__).with_name("students.db")
SUBJECTS = ["English", "Mathematics", "Science"]


def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                english REAL NOT NULL,
                mathematics REAL NOT NULL,
                science REAL NOT NULL
            )
        """)


def row_to_student(row):
    if row is None:
        return None
    marks = {
        "English": float(row["english"]),
        "Mathematics": float(row["mathematics"]),
        "Science": float(row["science"])
    }
    return {
        "student_id": row["student_id"],
        "name": row["name"],
        "marks": marks,
        "total": calculate_total(marks),
        "percentage": calculate_percentage(marks),
        "grade": calculate_grade(calculate_percentage(marks))
    }


def calculate_total(marks):
    return sum(marks.values())


def calculate_percentage(marks):
    return calculate_total(marks) / len(SUBJECTS)


def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"


# DSA: Linear Search - checks student IDs one by one.
def linear_search_student(students, student_id):
    for student in students:
        if student["student_id"] == student_id:
            return student
    return None


# DSA: Bubble Sort - highest total marks first.
def bubble_sort_students(students):
    ranked = students.copy()
    n = len(ranked)

    for i in range(n - 1):
        swapped = False
        for j in range(n - i - 1):
            if ranked[j]["total"] < ranked[j + 1]["total"]:
                ranked[j], ranked[j + 1] = ranked[j + 1], ranked[j]
                swapped = True
        if not swapped:
            break
    return ranked


def read_marks_from_form():
    marks = {}
    for subject, field in [
        ("English", "english"),
        ("Mathematics", "mathematics"),
        ("Science", "science")
    ]:
        try:
            value = float(request.form.get(field, ""))
        except ValueError:
            raise ValueError(f"Enter a valid number for {subject}.")
        if not 0 <= value <= 100:
            raise ValueError(f"{subject} marks must be between 0 and 100.")
        marks[subject] = value
    return marks


def fetch_all_students():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM students ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return [row_to_student(row) for row in rows]


@app.route("/")
def index():
    students = fetch_all_students()
    total_students = len(students)
    class_average = (
        sum(student["percentage"] for student in students) / total_students
        if total_students else 0
    )
    passed = sum(1 for student in students if student["percentage"] >= 40)
    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        class_average=class_average,
        passed=passed,
        query="",
        searched_student=None,
        ranked_students=bubble_sort_students(students)
    )


@app.route("/add", methods=["POST"])
def add_student():
    student_id = request.form.get("student_id", "").strip()
    name = request.form.get("name", "").strip()

    if not student_id or not name:
        flash("Student ID and name are required.", "error")
        return redirect(url_for("index"))

    try:
        marks = read_marks_from_form()
        with get_connection() as connection:
            connection.execute(
                """INSERT INTO students
                   (student_id, name, english, mathematics, science)
                   VALUES (?, ?, ?, ?, ?)""",
                (student_id, name, marks["English"],
                 marks["Mathematics"], marks["Science"])
            )
        flash(f"Student {name} added successfully.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except sqlite3.IntegrityError:
        flash("That student ID already exists. Use a unique ID.", "error")
    return redirect(url_for("index"))


@app.route("/search", methods=["GET"])
def search_student():
    query = request.args.get("student_id", "").strip()
    students = fetch_all_students()
    # Use the project's Linear Search algorithm for the lookup.
    found = linear_search_student(students, query) if query else None

    total_students = len(students)
    class_average = (
        sum(student["percentage"] for student in students) / total_students
        if total_students else 0
    )
    passed = sum(1 for student in students if student["percentage"] >= 40)
    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        class_average=class_average,
        passed=passed,
        query=query,
        searched_student=found,
        ranked_students=bubble_sort_students(students)
    )


@app.route("/update/<student_id>", methods=["POST"])
def update_student(student_id):
    name = request.form.get("name", "").strip()
    if not name:
        flash("Student name is required.", "error")
        return redirect(url_for("index"))

    try:
        marks = read_marks_from_form()
        with get_connection() as connection:
            result = connection.execute(
                """UPDATE students
                   SET name = ?, english = ?, mathematics = ?, science = ?
                   WHERE student_id = ?""",
                (name, marks["English"], marks["Mathematics"],
                 marks["Science"], student_id)
            )
        if result.rowcount:
            flash("Student record updated successfully.", "success")
        else:
            flash("Student not found.", "error")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/delete/<student_id>", methods=["POST"])
def delete_student(student_id):
    with get_connection() as connection:
        result = connection.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
    flash("Student record deleted." if result.rowcount else "Student not found.",
          "success" if result.rowcount else "error")
    return redirect(url_for("index"))


@app.route("/ranking")
def ranking():
    students = fetch_all_students()
    ranked_students = bubble_sort_students(students)
    total_students = len(students)
    class_average = (
        sum(student["percentage"] for student in students) / total_students
        if total_students else 0
    )
    passed = sum(1 for student in students if student["percentage"] >= 40)
    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        class_average=class_average,
        passed=passed,
        query="",
        searched_student=None,
        ranked_students=ranked_students,
        show_ranking=True
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
