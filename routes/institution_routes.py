from collections import Counter
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from models import (
    db, InstitutionProfile, StudentProfile, IndustryProfile,
    Opportunity, Application, Collaboration, Notification,
    StudentSkill, Skill, AssessmentAttempt
)
from auth import role_required, get_current_user
from helpers import calculate_career_readiness, calculate_skill_gaps

institution_bp = Blueprint('institution', __name__, url_prefix='/institution')

def get_current_institution():
    user = get_current_user()
    if user and user.role == 'institution':
        if not user.institution_profile:
            profile = InstitutionProfile(name="Demo University", admin_user_id=user.id)
            db.session.add(profile)
            db.session.commit()
        return user.institution_profile
    return None


# -----------------------------------------------------------------------------
# 1. INSTITUTION DASHBOARD
# -----------------------------------------------------------------------------
@institution_bp.route('/dashboard')
@role_required('institution')
def dashboard():
    inst = get_current_institution()
    
    # Calculate real statistics from database
    total_students = StudentProfile.query.count()
    
    # Students with >= 1 verified skill assessment
    assessed_students = db.session.query(StudentSkill.student_id).filter_by(is_verified=True).distinct().count()
    
    # Average career readiness across assessed students
    students = StudentProfile.query.all()
    readiness_scores = []
    gap_count = 0
    for s in students:
        r_info = calculate_career_readiness(s)
        readiness_scores.append(r_info['overall'])
        g_info = calculate_skill_gaps(s)
        if len(g_info['skills_to_improve']) > 0:
            gap_count += 1

    avg_readiness = int(round(sum(readiness_scores) / len(readiness_scores))) if readiness_scores else 0

    active_collabs = Collaboration.query.filter_by(status='Active').count()
    total_opps = Opportunity.query.count()
    total_apps = Application.query.count()
    selected_students = Application.query.filter_by(status='Selected').count()

    # Top skill gaps across students
    skill_gap_counter = Counter()
    for s in students:
        gaps = calculate_skill_gaps(s)
        for item in gaps['skills_to_improve']:
            skill_gap_counter[item['name']] += 1

    top_skill_gaps = skill_gap_counter.most_common(3)

    stats = {
        'total_students': total_students,
        'assessed_students': assessed_students,
        'avg_readiness': avg_readiness,
        'students_with_gaps': gap_count,
        'active_collabs': active_collabs,
        'total_opportunities': total_opps,
        'total_applications': total_apps,
        'placed_students': selected_students,
        'top_skill_gaps': top_skill_gaps
    }

    return render_template(
        'institution/dashboard.html',
        institution=inst,
        stats=stats
    )


# -----------------------------------------------------------------------------
# 2. STUDENTS DIRECTORY & SEARCH
# -----------------------------------------------------------------------------
@institution_bp.route('/students')
@role_required('institution')
def students():
    inst = get_current_institution()
    
    search_query = request.args.get('search', '').strip().lower()
    branch_filter = request.args.get('branch', '').strip()
    year_filter = request.args.get('year', '').strip()
    readiness_filter = request.args.get('readiness', '').strip()

    query = StudentProfile.query
    if search_query:
        query = query.filter(StudentProfile.name_display.ilike(f"%{search_query}%"))
    if branch_filter:
        query = query.filter(StudentProfile.branch == branch_filter)
    if year_filter:
        query = query.filter(StudentProfile.year == year_filter)

    all_students = query.all()
    students_data = []

    for s in all_students:
        r_info = calculate_career_readiness(s)
        attempts_count = s.attempts.count()
        latest_app = s.applications.order_by(Application.submitted_date.desc()).first()
        app_status = latest_app.status if latest_app else "Not Applied"

        # Filter readiness
        overall = r_info['overall']
        if readiness_filter == 'low' and overall >= 40:
            continue
        elif readiness_filter == 'mid' and not (40 <= overall < 70):
            continue
        elif readiness_filter == 'high' and overall < 70:
            continue

        students_data.append({
            'student': s,
            'career_readiness': overall,
            'assessments_count': attempts_count,
            'internship_status': app_status
        })

    branches = sorted(list(set(s.branch for s in StudentProfile.query.all())))
    years = sorted(list(set(s.year for s in StudentProfile.query.all())))

    return render_template(
        'institution/students.html',
        institution=inst,
        students=students_data,
        branches=branches,
        years=years,
        active_branch=branch_filter,
        active_year=year_filter,
        active_readiness=readiness_filter,
        search_query=search_query
    )


# -----------------------------------------------------------------------------
# 3. INDUSTRY PARTNERSHIPS
# -----------------------------------------------------------------------------
@institution_bp.route('/industry')
@role_required('institution')
def industry():
    inst = get_current_institution()
    companies = IndustryProfile.query.all()
    partners_data = []

    for comp in companies:
        opps_count = comp.opportunities.count()
        collabs_count = comp.user.academician_profile.collaborations.count() if hasattr(comp.user, 'academician_profile') and comp.user.academician_profile else Collaboration.query.filter_by(industry_id=comp.id).count()
        apps_received = Application.query.filter_by(company_id=comp.id).count()
        active_interns = Application.query.filter_by(company_id=comp.id, status='Selected').count()

        partners_data.append({
            'company': comp,
            'opportunities_count': opps_count,
            'collaborations_count': collabs_count,
            'applications_count': apps_received,
            'active_internships': active_interns,
            'recent_opps': comp.opportunities.limit(2).all()
        })

    return render_template(
        'institution/industry.html',
        institution=inst,
        partners=partners_data
    )


# -----------------------------------------------------------------------------
# 4. INSTITUTION ANALYTICS (REAL DATABASE DATA CHARTS)
# -----------------------------------------------------------------------------
@institution_bp.route('/analytics')
@role_required('institution')
def analytics():
    inst = get_current_institution()
    students = StudentProfile.query.all()

    # Chart 1: Common Skill Gaps
    skill_gap_counter = Counter()
    for s in students:
        gaps = calculate_skill_gaps(s)
        for item in gaps['skills_to_improve']:
            skill_gap_counter[item['name']] += 1

    chart1_labels = [k for k, v in skill_gap_counter.most_common(6)]
    chart1_data = [v for k, v in skill_gap_counter.most_common(6)]

    # Chart 2: Career Goal Distribution
    goal_counter = Counter(s.career_goal for s in students if s.career_goal)
    chart2_labels = list(goal_counter.keys())
    chart2_data = list(goal_counter.values())

    # Chart 3: Assessment Completion
    assessed_count = sum(1 for s in students if s.skills.filter_by(is_verified=True).count() > 0)
    unassessed_count = len(students) - assessed_count
    chart3_labels = ["Assessed (≥1 Skill)", "Not Assessed"]
    chart3_data = [assessed_count, unassessed_count]

    # Chart 4: Internship Participation
    selected_count = Application.query.filter_by(status='Selected').count()
    applied_count = Application.query.filter(Application.status != 'Selected').count()
    not_applied_count = max(0, len(students) - (selected_count + applied_count))
    chart4_labels = ["Selected / Placed", "In Review / Interview", "Not Applied"]
    chart4_data = [selected_count, applied_count, not_applied_count]

    # Chart 5: Career Readiness Distribution
    bins = {"0-30%": 0, "30-60%": 0, "60-90%": 0, "90-100%": 0}
    for s in students:
        r = calculate_career_readiness(s)['overall']
        if r < 30:
            bins["0-30%"] += 1
        elif r < 60:
            bins["30-60%"] += 1
        elif r < 90:
            bins["60-90%"] += 1
        else:
            bins["90-100%"] += 1

    chart5_labels = list(bins.keys())
    chart5_data = list(bins.values())

    # Chart 6: Industry Demanded Skills
    opp_skills_counter = Counter()
    all_opps = Opportunity.query.all()
    for opp in all_opps:
        for sk in opp.required_skills:
            opp_skills_counter[sk] += 1

    chart6_labels = [k for k, v in opp_skills_counter.most_common(6)]
    chart6_data = [v for k, v in opp_skills_counter.most_common(6)]

    analytics_data = {
        'chart1': {'labels': chart1_labels, 'data': chart1_data},
        'chart2': {'labels': chart2_labels, 'data': chart2_data},
        'chart3': {'labels': chart3_labels, 'data': chart3_data},
        'chart4': {'labels': chart4_labels, 'data': chart4_data},
        'chart5': {'labels': chart5_labels, 'data': chart5_data},
        'chart6': {'labels': chart6_labels, 'data': chart6_data}
    }

    return render_template(
        'institution/analytics.html',
        institution=inst,
        analytics=analytics_data
    )


# -----------------------------------------------------------------------------
# 5. NOTIFICATIONS
# -----------------------------------------------------------------------------
@institution_bp.route('/notifications')
@role_required('institution')
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    return render_template(
        'institution/notifications.html',
        notifications=notifs,
        unread_count=unread_count
    )
