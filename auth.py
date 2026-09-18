import datetime
from functools import wraps
import bcrypt
import jwt
from flask import session, request, redirect, url_for, flash, jsonify, g
from config import Config
from models import User, db

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def generate_jwt_token(user: User) -> str:
    """Generate a signed JWT token valid for 7 days."""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=Config.JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def decode_jwt_token(token: str):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user():
    """Retrieve current logged in user from session, cookie, or Authorization header."""
    if hasattr(g, 'current_user') and g.current_user is not None:
        return g.current_user

    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            g.current_user = user
            return user

    # Check JWT cookie
    token = request.cookies.get('auth_token')
    
    # Check Authorization header if not in cookie
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

    if token:
        payload = decode_jwt_token(token)
        if payload:
            user = db.session.get(User, payload.get('user_id'))
            if user and user.role == payload.get('role'):
                session['user_id'] = user.id
                session['role'] = user.role
                session['email'] = user.email
                g.current_user = user
                return user

    g.current_user = None
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Authentication required.'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.path))
            
            if user.role not in allowed_roles:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Access forbidden: unauthorized role.'}), 403
                flash('You do not have permission to access that section.', 'danger')
                # Redirect to appropriate role dashboard
                if user.role == 'student':
                    return redirect(url_for('student.profile'))
                elif user.role == 'industry':
                    return redirect(url_for('industry.profile'))
                elif user.role == 'academician':
                    return redirect(url_for('academician.profile'))
                elif user.role == 'institution':
                    return redirect(url_for('institution.dashboard'))
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

DEMO_ACCOUNTS = {
    'student': {
        'email': 'student@demo.skillbridge.local',
        'password': 'Demo@123',
        'display_name': 'Student 123'
    },
    'industry': {
        'email': 'industry@demo.skillbridge.local',
        'password': 'Demo@123',
        'display_name': 'Demo Tech Solutions'
    },
    'academician': {
        'email': 'academician@demo.skillbridge.local',
        'password': 'Demo@123',
        'display_name': 'Dr. A. Sharma'
    },
    'institution': {
        'email': 'institution@demo.skillbridge.local',
        'password': 'Demo@123',
        'display_name': 'Demo University Admin'
    }
}
