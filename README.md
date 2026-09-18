# SkillBridge

SkillBridge is a local Flask prototype for connecting students, industry partners, academicians, and institutions through verified skills, learning resources, opportunities, applications, and notifications.

## Stack

- Python 3.11+ and Flask
- Flask-SQLAlchemy with SQLite
- Jinja2, Bootstrap 5, vanilla JavaScript, and Chart.js
- bcrypt password hashing and JWT session cookies

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a private `JWT_SECRET`.
4. Start the app with `python app.py`.
5. Open `http://127.0.0.1:5000`.

On Windows, you can double-click `start_localhost.bat` instead. It starts the local service and opens `http://localhost:5000` automatically.

The first startup creates and seeds an empty SQLite database automatically. To reset the local database and reseed it deterministically, run `python seed_data.py`.

## Demo accounts

All demo accounts use `Demo@123`.

- Student: `student@demo.skillbridge.local`
- Industry: `industry@demo.skillbridge.local`
- Academician: `academician@demo.skillbridge.local`
- Institution: `institution@demo.skillbridge.local`

Choose a demo portal from the public login page. After sign-in, each role has exactly five primary navigation areas and role-protected routes.

## Environment

`.env.example` documents `NODE_ENV`, `DB_URL`, `API_PORT`, `JWT_SECRET`, and `FRONTEND_PORT`. `DB_URL` defaults to a local SQLite file and no external database service is required.

## Deployment

The production WSGI object is exported from `wsgi.py` as `app`. Use `gunicorn wsgi:app` or the included `Procfile`. Platforms that autodetect Flask can also use `app:app`.

For local troubleshooting, use `python app.py`. The server binds to `0.0.0.0` and uses `API_PORT` when provided, defaulting to `5000`. Debug reloading is disabled by default; set `FLASK_DEBUG=1` only for development debugging.