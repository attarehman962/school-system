# School System CRUD (LAPP Stack)

This is a simple **School System** CRUD project with 3 entities:

- **Teacher** (can teach many classes)
- **Class** (can have one teacher and many students)
- **Student** (can belong to one class)

Tech stack:

- **Linux**
- **Apache** (deployment via `mod_wsgi`)
- **PostgreSQL**
- **Python (Flask + SQLAlchemy)**

## Data model

- `teachers`: `first_name`, `last_name`, `email` (unique), `phone`, `hire_date`
- `classes`: `name`, `grade_level`, `room`, `school_year`, `teacher_id` (nullable)
- `students`: `first_name`, `last_name`, `email` (unique, nullable), `date_of_birth`, `enrollment_date`, `class_id` (nullable)

## 1) Create a PostgreSQL database

Example (as postgres user):

```bash
createdb school_db
```

Or SQL:

```sql
CREATE DATABASE school_db;
```

## 2) Configure environment

Copy `.env.example` to `.env` and update it:

```bash
cp .env.example .env
```

**Option A – PostgreSQL (for LAPP):**

- Ensure PostgreSQL is running and the database exists (e.g. `createdb school_db`).
- Set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/school_db`.

**Option B – SQLite (no PostgreSQL needed):**

- In `.env`, set `USE_SQLITE=1` and remove or comment out `DATABASE_URL`.
- Data is stored in `instance/school.db`. Use this for local development if PostgreSQL is not running.

## 3) Install and run (development)

Activate your venv and install:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Open:

- Home: `http://127.0.0.1:5000/`
- Teachers: `/teachers`
- Classes: `/classes`
- Students: `/students`

Create tables (first time):

- Click **Create DB tables** on the home page, or:

```bash
curl -X POST http://127.0.0.1:5000/init-db
```

## 4) Apache (mod_wsgi) deployment notes

You already have `wsgi.py`:

- `wsgi.py` exposes `application` for Apache.

Example Apache site config (adjust paths/user):

```apacheconf
<VirtualHost *:80>
    ServerName school.local

    WSGIDaemonProcess schoolapp python-home=/home/atta/Documents/python/python-project/venv python-path=/home/atta/Documents/python/python-project
    WSGIProcessGroup schoolapp
    WSGIScriptAlias / /home/atta/Documents/python/python-project/wsgi.py

    <Directory /home/atta/Documents/python/python-project>
        Require all granted
    </Directory>

    # Provide env vars to mod_wsgi
    SetEnv DATABASE_URL "postgresql+psycopg://postgres:postgres@localhost:5432/school_db"
    SetEnv SECRET_KEY "change-me"
</VirtualHost>
```

Then enable the site + reload Apache.

## Database connection errors

If you see **"Database connection error"** or **"connection refused"**:

- **PostgreSQL:** Start the server (e.g. `sudo systemctl start postgresql`) and ensure the database and `DATABASE_URL` are correct.
- **Or use SQLite:** In `.env` set `USE_SQLITE=1` and leave `DATABASE_URL` unset (or comment it out). The app will use `instance/school.db`.

