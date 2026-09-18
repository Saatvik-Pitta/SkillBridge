import os
from flask import Flask, redirect, url_for, send_from_directory, render_template, request
from config import Config
from models import db, Notification
from auth import get_current_user, DEMO_ACCOUNTS
from routes import auth_bp, student_bp, industry_bp, academician_bp, institution_bp

# Explicit module-level Flask instance for deployment autodetection.
app = Flask(__name__)


def create_app(config_class=Config, flask_app=None):
    app = flask_app or Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(industry_bp)
    app.register_blueprint(academician_bp)
    app.register_blueprint(institution_bp)

    # Context processors for global template variables
    @app.context_processor
    def inject_globals():
        user = get_current_user()
        unread_count = 0
        if user:
            unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
        return {
            'current_user': user,
            'active_role': user.role if user else None,
            'unread_notifications_count': unread_count,
            'demo_accounts': DEMO_ACCOUNTS
        }

    # Root route: redirect based on login status
    @app.route('/')
    def index():
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        if user.role == 'student':
            return redirect(url_for('student.profile'))
        elif user.role == 'industry':
            return redirect(url_for('industry.profile'))
        elif user.role == 'academician':
            return redirect(url_for('academician.profile'))
        elif user.role == 'institution':
            return redirect(url_for('institution.dashboard'))
        return redirect(url_for('auth.login'))

    # Route to securely serve uploaded student resumes
    @app.route('/storage/resumes/<path:filename>')
    def serve_resume(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', error_title="404 - Page Not Found", error_message="The requested resource or section could not be located."), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('base.html', error_title="403 - Forbidden Access", error_message="You do not have permission to view or manage this role section."), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('base.html', error_title="500 - Server Error", error_message="An internal system error occurred. Please refresh or contact support."), 500

    # Initialize the schema and seed demo data on the first empty run.
    with app.app_context():
        db.create_all()
        from models import User
        from seed_data import ensure_assessment_catalog
        if User.query.first() is None:
            from seed_data import seed_database
            seed_database(app, reset=False)
        ensure_assessment_catalog(app)

    return app


# Configure the explicit module-level instance for local and hosted use.
create_app(Config, app)


if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5000))
    print(f"SkillBridge starting on http://127.0.0.1:{port}")
    debug = os.environ.get('FLASK_DEBUG', '').lower() in {'1', 'true', 'yes'}
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
