import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from models import db, User, StudentProfile, IndustryProfile, AcademicianProfile, InstitutionProfile
from auth import hash_password, check_password, generate_jwt_token, get_current_user, DEMO_ACCOUNTS

auth_bp = Blueprint('auth', __name__)

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)."
    return True, ""

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    current_user = get_current_user()
    if current_user:
        return redirect_to_role_dashboard(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html', email=email, demo_accounts=DEMO_ACCOUNTS)

        user = User.query.filter_by(email=email).first()
        if not user or not check_password(password, user.password_hash):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', email=email, demo_accounts=DEMO_ACCOUNTS)

        # Successful login
        session['user_id'] = user.id
        session['role'] = user.role
        session['email'] = user.email

        token = generate_jwt_token(user)
        next_url = request.args.get('next')
        response = redirect(next_url if next_url else url_for_role_dashboard(user.role))
        response.set_cookie('auth_token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
        flash(f'Welcome back, {get_user_display_name(user)}!', 'success')
        return response

    return render_template('auth/login.html', demo_accounts=DEMO_ACCOUNTS)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    current_user = get_current_user()
    if current_user:
        return redirect_to_role_dashboard(current_user.role)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '').strip().lower()

        # Validation
        if not all([name, email, password, confirm_password, role]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        if role not in ['student', 'industry', 'academician', 'institution']:
            flash('Please select a valid account role.', 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register.html', name=name, email=email, role=role)

        # Create user
        new_user = User(
            email=email,
            password_hash=hash_password(password),
            role=role
        )
        db.session.add(new_user)
        db.session.flush()

        # Create role profile
        if role == 'student':
            profile = StudentProfile(user_id=new_user.id, name_display=name)
            db.session.add(profile)
        elif role == 'industry':
            profile = IndustryProfile(user_id=new_user.id, company_name=name)
            db.session.add(profile)
        elif role == 'academician':
            profile = AcademicianProfile(user_id=new_user.id, name_display=name)
            db.session.add(profile)
        elif role == 'institution':
            profile = InstitutionProfile(name=name, admin_user_id=new_user.id)
            db.session.add(profile)

        db.session.commit()

        # Log in newly registered user
        session['user_id'] = new_user.id
        session['role'] = new_user.role
        session['email'] = new_user.email

        token = generate_jwt_token(new_user)
        response = redirect(url_for_role_dashboard(role))
        response.set_cookie('auth_token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
        flash('Account registered successfully! Welcome to SkillBridge.', 'success')
        return response

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    response = redirect(url_for('auth.login'))
    response.delete_cookie('auth_token')
    flash('You have been logged out safely.', 'info')
    return response


@auth_bp.route('/switch-role/<target_role>')
def switch_role(target_role):
    """
    Role Switching Behavior (from specification):
    Logs out the current user and logs in the selected demo account immediately,
    updates JWT token and redirects to that role's dashboard.
    """
    target_role = target_role.lower().strip()
    if target_role not in DEMO_ACCOUNTS:
        flash('Unknown demo role requested.', 'danger')
        return redirect(url_for('auth.login'))

    demo_email = DEMO_ACCOUNTS[target_role]['email']
    user = User.query.filter_by(email=demo_email).first()

    if not user:
        flash(f'Demo user for {target_role} is not initialized.', 'warning')
        return redirect(url_for('auth.login'))

    session.clear()
    session['user_id'] = user.id
    session['role'] = user.role
    session['email'] = user.email

    token = generate_jwt_token(user)
    response = redirect(url_for_role_dashboard(user.role))
    response.set_cookie('auth_token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
    flash(f'Switched active role to {user.role.capitalize()} ({DEMO_ACCOUNTS[target_role]["display_name"]}).', 'info')
    return response


@auth_bp.route('/api/auth/verify', methods=['GET'])
def verify_token():
    user = get_current_user()
    if user:
        return jsonify({
            'authenticated': True,
            'user': user.to_dict(),
            'display_name': get_user_display_name(user)
        })
    return jsonify({'authenticated': False}), 401


def get_user_display_name(user: User) -> str:
    if user.role == 'student' and user.student_profile:
        return user.student_profile.name_display
    elif user.role == 'industry' and user.industry_profile:
        return user.industry_profile.company_name
    elif user.role == 'academician' and user.academician_profile:
        return user.academician_profile.name_display
    elif user.role == 'institution' and user.institution_profile:
        return user.institution_profile.name
    return user.email.split('@')[0]

def url_for_role_dashboard(role: str) -> str:
    if role == 'student':
        return url_for('student.profile')
    elif role == 'industry':
        return url_for('industry.profile')
    elif role == 'academician':
        return url_for('academician.profile')
    elif role == 'institution':
        return url_for('institution.dashboard')
    return url_for('auth.login')

def redirect_to_role_dashboard(role: str):
    return redirect(url_for_role_dashboard(role))
