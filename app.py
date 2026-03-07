import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import OperationalError

from database import Class, Student, Teacher, db, init_app

# Load .env from project root so USE_SQLITE and DATABASE_URL are always from this file
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(_env_path)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

init_app(app)


@app.errorhandler(OperationalError)
def handle_db_error(e):
    msg = getattr(e.orig, "message", str(e)) if getattr(e, "orig", None) else str(e)
    return render_template("db_error.html", message=msg), 503


def _parse_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/init-db", methods=["POST"])
def init_db():
    db.create_all()
    flash("Database tables created (if they did not exist).", "success")
    return redirect(url_for("home"))


# -------------------------
# Teachers CRUD
# -------------------------
@app.route("/teachers")
def teachers_list():
    teachers = Teacher.query.order_by(Teacher.last_name.asc(), Teacher.first_name.asc()).all()
    return render_template("teachers/list.html", teachers=teachers)


@app.route("/teachers/new", methods=["GET", "POST"])
def teachers_create():
    if request.method == "POST":
        teacher = Teacher(
            first_name=request.form.get("first_name", "").strip(),
            last_name=request.form.get("last_name", "").strip(),
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip() or None,
            hire_date=_parse_date(request.form.get("hire_date", "").strip()),
        )
        if not teacher.first_name or not teacher.last_name or not teacher.email:
            flash("First name, last name, and email are required.", "error")
            return render_template("teachers/form.html", teacher=teacher, mode="create")
        db.session.add(teacher)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not create teacher (email may already exist).", "error")
            return render_template("teachers/form.html", teacher=teacher, mode="create")
        flash("Teacher created.", "success")
        return redirect(url_for("teachers_list"))

    return render_template("teachers/form.html", teacher=None, mode="create")


@app.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
def teachers_edit(teacher_id: int):
    teacher = Teacher.query.get_or_404(teacher_id)
    if request.method == "POST":
        teacher.first_name = request.form.get("first_name", "").strip()
        teacher.last_name = request.form.get("last_name", "").strip()
        teacher.email = request.form.get("email", "").strip()
        teacher.phone = request.form.get("phone", "").strip() or None
        teacher.hire_date = _parse_date(request.form.get("hire_date", "").strip())
        if not teacher.first_name or not teacher.last_name or not teacher.email:
            flash("First name, last name, and email are required.", "error")
            return render_template("teachers/form.html", teacher=teacher, mode="edit")
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not update teacher (email may already exist).", "error")
            return render_template("teachers/form.html", teacher=teacher, mode="edit")
        flash("Teacher updated.", "success")
        return redirect(url_for("teachers_list"))

    return render_template("teachers/form.html", teacher=teacher, mode="edit")


@app.route("/teachers/<int:teacher_id>/delete", methods=["POST"])
def teachers_delete(teacher_id: int):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash("Teacher deleted.", "success")
    return redirect(url_for("teachers_list"))


# -------------------------
# Classes CRUD
# -------------------------
@app.route("/classes")
def classes_list():
    classes = Class.query.order_by(Class.name.asc()).all()
    return render_template("classes/list.html", classes=classes)


@app.route("/classes/new", methods=["GET", "POST"])
def classes_create():
    teachers = Teacher.query.order_by(Teacher.last_name.asc()).all()
    if request.method == "POST":
        teacher_id = request.form.get("teacher_id") or None
        class_ = Class(
            name=request.form.get("name", "").strip(),
            grade_level=request.form.get("grade_level", "").strip() or None,
            room=request.form.get("room", "").strip() or None,
            school_year=request.form.get("school_year", "").strip() or None,
            teacher_id=int(teacher_id) if teacher_id else None,
        )
        if not class_.name:
            flash("Class name is required.", "error")
            return render_template("classes/form.html", class_=class_, mode="create", teachers=teachers)
        db.session.add(class_)
        db.session.commit()
        flash("Class created.", "success")
        return redirect(url_for("classes_list"))

    return render_template("classes/form.html", class_=None, mode="create", teachers=teachers)


@app.route("/classes/<int:class_id>/edit", methods=["GET", "POST"])
def classes_edit(class_id: int):
    class_ = Class.query.get_or_404(class_id)
    teachers = Teacher.query.order_by(Teacher.last_name.asc()).all()
    if request.method == "POST":
        teacher_id = request.form.get("teacher_id") or None
        class_.name = request.form.get("name", "").strip()
        class_.grade_level = request.form.get("grade_level", "").strip() or None
        class_.room = request.form.get("room", "").strip() or None
        class_.school_year = request.form.get("school_year", "").strip() or None
        class_.teacher_id = int(teacher_id) if teacher_id else None
        if not class_.name:
            flash("Class name is required.", "error")
            return render_template("classes/form.html", class_=class_, mode="edit", teachers=teachers)
        db.session.commit()
        flash("Class updated.", "success")
        return redirect(url_for("classes_list"))

    return render_template("classes/form.html", class_=class_, mode="edit", teachers=teachers)


@app.route("/classes/<int:class_id>/delete", methods=["POST"])
def classes_delete(class_id: int):
    class_ = Class.query.get_or_404(class_id)
    db.session.delete(class_)
    db.session.commit()
    flash("Class deleted.", "success")
    return redirect(url_for("classes_list"))


# -------------------------
# Students CRUD
# -------------------------
@app.route("/students")
def students_list():
    students = Student.query.order_by(Student.last_name.asc(), Student.first_name.asc()).all()
    return render_template("students/list.html", students=students)


@app.route("/students/new", methods=["GET", "POST"])
def students_create():
    classes = Class.query.order_by(Class.name.asc()).all()
    if request.method == "POST":
        class_id = request.form.get("class_id") or None
        student = Student(
            first_name=request.form.get("first_name", "").strip(),
            last_name=request.form.get("last_name", "").strip(),
            email=request.form.get("email", "").strip() or None,
            date_of_birth=_parse_date(request.form.get("date_of_birth", "").strip()),
            enrollment_date=_parse_date(request.form.get("enrollment_date", "").strip()),
            class_id=int(class_id) if class_id else None,
        )
        if not student.first_name or not student.last_name:
            flash("First name and last name are required.", "error")
            return render_template("students/form.html", student=student, mode="create", classes=classes)
        db.session.add(student)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not create student (email may already exist).", "error")
            return render_template("students/form.html", student=student, mode="create", classes=classes)
        flash("Student created.", "success")
        return redirect(url_for("students_list"))

    return render_template("students/form.html", student=None, mode="create", classes=classes)


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def students_edit(student_id: int):
    student = Student.query.get_or_404(student_id)
    classes = Class.query.order_by(Class.name.asc()).all()
    if request.method == "POST":
        class_id = request.form.get("class_id") or None
        student.first_name = request.form.get("first_name", "").strip()
        student.last_name = request.form.get("last_name", "").strip()
        student.email = request.form.get("email", "").strip() or None
        student.date_of_birth = _parse_date(request.form.get("date_of_birth", "").strip())
        student.enrollment_date = _parse_date(request.form.get("enrollment_date", "").strip())
        student.class_id = int(class_id) if class_id else None
        if not student.first_name or not student.last_name:
            flash("First name and last name are required.", "error")
            return render_template("students/form.html", student=student, mode="edit", classes=classes)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Could not update student (email may already exist).", "error")
            return render_template("students/form.html", student=student, mode="edit", classes=classes)
        flash("Student updated.", "success")
        return redirect(url_for("students_list"))

    return render_template("students/form.html", student=student, mode="edit", classes=classes)


@app.route("/students/<int:student_id>/delete", methods=["POST"])
def students_delete(student_id: int):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("students_list"))


if __name__ == "__main__":
    app.run(debug=True)