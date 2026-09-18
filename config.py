import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skillbridge-flask-session-key-dev-2026')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'skillbridge-jwt-secure-key-778899')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DAYS = 7
    
    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL', f"sqlite:///{os.path.join(BASE_DIR, 'skillbridge.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'storage', 'resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max
    ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
