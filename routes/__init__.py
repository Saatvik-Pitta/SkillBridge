from .auth_routes import auth_bp
from .student_routes import student_bp
from .industry_routes import industry_bp
from .academician_routes import academician_bp
from .institution_routes import institution_bp

__all__ = ['auth_bp', 'student_bp', 'industry_bp', 'academician_bp', 'institution_bp']
