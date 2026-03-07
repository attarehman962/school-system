import os
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    classes = db.relationship("Class", back_populates="teacher", cascade="all, delete", passive_deletes=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Class(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    grade_level = db.Column(db.String(20), nullable=True)
    room = db.Column(db.String(20), nullable=True)
    school_year = db.Column(db.String(20), nullable=True)  # e.g. "2025/2026"
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True, index=True)
    teacher = db.relationship("Teacher", back_populates="classes")

    students = db.relationship("Student", back_populates="class_", cascade="all, delete", passive_deletes=True)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    enrollment_date = db.Column(db.Date, nullable=True, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    class_id = db.Column(db.Integer, db.ForeignKey("classes.id", ondelete="SET NULL"), nullable=True, index=True)
    class_ = db.relationship("Class", back_populates="students")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


def init_app(app):
    """
    Configure SQLAlchemy using DATABASE_URL (preferred), PG* env vars, or SQLite fallback.
    - Set DATABASE_URL for PostgreSQL: postgresql+psycopg://user:pass@host:port/dbname
    - Set USE_SQLITE=1 or leave DATABASE_URL unset to use SQLite (instance/school.db)
    """
    use_sqlite = os.getenv("USE_SQLITE", "").strip().lower() in ("1", "true", "yes")
    database_url = (os.getenv("DATABASE_URL") or "").strip()

    # Prefer SQLite when USE_SQLITE is set (ignores DATABASE_URL so no wrong password)
    if use_sqlite or not database_url:
        instance_path = app.instance_path
        os.makedirs(instance_path, exist_ok=True)
        database_url = f"sqlite:///{os.path.join(instance_path, 'school.db')}"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
