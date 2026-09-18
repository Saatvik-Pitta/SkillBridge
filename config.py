import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skillbridge-flask-session-key-dev-2026')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'skillbridge-jwt-secure-key-778899')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DAYS = 7
    
    # SQLite Database URI
    # Vercel's deployed bundle is read-only. Use its writable temporary directory
    # for the prototype database and uploads when running as a serverless function.
    DEFAULT_DB_PATH = os.path.join('/tmp' if IS_VERCEL else BASE_DIR, 'skillbridge.db')
    raw_db_url = os.environ.get('DATABASE_URL') or os.environ.get('DB_URL', f"sqlite:///{DEFAULT_DB_PATH}")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join('/tmp' if IS_VERCEL else BASE_DIR, 'storage', 'resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max
    ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
