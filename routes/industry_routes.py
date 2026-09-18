import json
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    jsonify
)
from models import (
    db, IndustryProfile, Opportunity, Application,
    StudentProfile, Skill, Notification
)
from auth import role_required, get_current_user
from helpers import (
    calculate_skill_match, create_notification, record_profile_view
)

industry_bp = Blueprint('industry', __name__, url_prefix='/industry')

def get_current_industry():
    user = get_current_user()
    if user and user.role == 'industry':
        if not user.industry_profile:
            profile = IndustryProfile(user_id=user.id, company_name="Demo Tech Solutions")
            db.session.add(profile)
            db.session.commit()
        return user.industry_profile
    return None


# -----------------------------------------------------------------------------
# 1. COMPANY PROFILE
# -----------------------------------------------------------------------------
@industry_bp.route('/profile')
@role_required('industry')
def profile():
    company = get_current_industry()
    all_skills = Skill.query.order_by(Skill.name).all()

    # Dashboard overview numbers (calculated from database)
    opps_count = company.opportunities.count()
    apps_received = Application.query.filter_by(company_id=company.id).count()
    shortlisted_count = Application.query.filter_by(company_id=company.id, status='Shortlisted').count()
    interview_count = Application.query.filter_by(company_id=company.id, status='Interview').count()
    selected_count = Application.query.filter_by(company_id=company.id, status='Selected').count()

    stats = {
        'opps_count': opps_count,
        'apps_received': apps_received,
        'shortlisted_count': shortlisted_count,
        'interview_count': interview_count,
        'selected_count': selected_count
    }

    return render_template(
        'industry/profile.html',
        company=company,
        stats=stats,
        all_skills=all_skills
    )


@industry_bp.route('/profile/update', methods=['POST'])
@role_required('industry')
def update_profile():
    company = get_current_industry()
    
    company.company_name = request.form.get('company_name', company.company_name).strip()
    company.industry = request.form.get('industry', company.industry).strip()
    company.company_size = request.form.get('company_size', company.company_size).strip()
    company.location = request.form.get('location', company.location).strip()
    company.website = request.form.get('website', company.website).strip()
    company.description = request.form.get('description', company.description).strip()
    
    company.hiring_interests = request.form.getlist('hiring_interests')
    company.commonly_required_skills = request.form.getlist('commonly_required_skills')
    company.collaboration_interests = request.form.getlist('collaboration_interests')

    db.session.commit()
    flash('Company profile saved successfully.', 'success')
    return redirect(url_for('industry.profile'))


# -----------------------------------------------------------------------------
# 2. OPPORTUNITIES (CREATE & MANAGE)
# -----------------------------------------------------------------------------
@industry_bp.route('/opportunities')
@role_required('industry')
def opportunities():
    company = get_current_industry()
    opps = company.opportunities.order_by(Opportunity.created_at.desc()).all()
    all_skills = Skill.query.order_by(Skill.name).all()

    # Precalculate application metrics per opportunity
    opps_data = []
    for opp in opps:
        total_apps = opp.applications.count()
        shortlisted = opp.applications.filter_by(status='Shortlisted').count()
        interviews = opp.applications.filter_by(status='Interview').count()
        selected = opp.applications.filter_by(status='Selected').count()
        opps_data.append({
            'opp': opp,
            'total_apps': total_apps,
            'shortlisted': shortlisted,
            'interviews': interviews,
            'selected': selected
        })

    return render_template(
        'industry/opportunities.html',
        company=company,
        opps_data=opps_data,
        all_skills=all_skills
    )


@industry_bp.route('/opportunities/create', methods=['POST'])
@role_required('industry')
def create_opportunity():
    company = get_current_industry()
    title = request.form.get('title', '').strip()
    opp_type = request.form.get('opportunity_type', 'internship').strip()
    description = request.form.get('description', '').strip()
    location = request.form.get('location', company.location).strip()
    work_mode = request.form.get('work_mode', 'Hybrid')
    duration = request.form.get('duration', '3 months').strip()
    experience_level = request.form.get('experience_level', 'Fresher').strip()
    eligibility = request.form.get('eligibility', '2nd-4th year students').strip()
    deadline = request.form.get('deadline', '').strip()
    stipend = request.form.get('stipend_salary', '').strip()
    action = request.form.get('action', 'publish')

    required_skills = request.form.getlist('required_skills')
    skill_levels = request.form.getlist('skill_levels')
    if not skill_levels:
        skill_levels = ['intermediate'] * len(required_skills)

    # Dynamic application questions
    q_texts = request.form.getlist('question_texts')
    q_reqs = request.form.getlist('question_required')
    questions = []
    for i, q_text in enumerate(q_texts):
        if q_text.strip():
            questions.append({
                'id': i + 1,
                'question_text': q_text.strip(),
                'is_required': str(i) in q_reqs or True
            })

    if not title or not description or not deadline or not required_skills:
        flash('Please fill in all required fields (title, description, required skills, deadline).', 'danger')
        return redirect(url_for('industry.opportunities'))

    opp = Opportunity(
        company_id=company.id,
        company_name=company.company_name,
        title=title,
        description=description,
        opportunity_type=opp_type,
        location=location,
        work_mode=work_mode,
        duration=duration,
        experience_level=experience_level,
        eligibility=eligibility,
        deadline=deadline,
        stipend_salary=stipend or 'Not specified',
        status='published' if action == 'publish' else 'draft',
        source_url=company.website
    )
    opp.required_skills = required_skills
    opp.required_skill_levels = skill_levels
    opp.application_questions = questions

    db.session.add(opp)
    db.session.commit()

    flash(f"Opportunity '{title}' {'published' if action == 'publish' else 'saved as draft'}.", 'success')
    return redirect(url_for('industry.opportunities'))


@industry_bp.route('/opportunities/<int:id>/status', methods=['POST'])
@role_required('industry')
def toggle_opportunity_status(id):
    company = get_current_industry()
    opp = Opportunity.query.filter_by(id=id, company_id=company.id).first_or_404()
    new_status = request.form.get('status', 'closed')
    if new_status in ['published', 'draft', 'closed']:
        opp.status = new_status
        db.session.commit()
        flash(f"Opportunity status updated to {new_status}.", 'info')
    return redirect(url_for('industry.opportunities'))


@industry_bp.route('/opportunities/<int:id>/delete', methods=['POST'])
@role_required('industry')
def delete_opportunity(id):
    company = get_current_industry()
    opp = Opportunity.query.filter_by(id=id, company_id=company.id).first_or_404()
    db.session.delete(opp)
    db.session.commit()
    flash('Opportunity removed.', 'info')
    return redirect(url_for('industry.opportunities'))


# -----------------------------------------------------------------------------
# 3. CANDIDATES SEARCH & DISCOVERY
# -----------------------------------------------------------------------------
@industry_bp.route('/candidates')
@role_required('industry')
def candidates():
    company = get_current_industry()
    opps = company.opportunities.filter_by(status='published').all()
    all_skills = Skill.query.order_by(Skill.name).all()

    # Filter parameters
    selected_opp_id = request.args.get('opportunity_id', type=int)
    search_name = request.args.get('name', '').strip().lower()
    skill_id = request.args.get('skill_id', type=int)
    min_cgpa = request.args.get('min_cgpa', type=float)
    career_goal = request.args.get('career_goal', '').strip()

    # Selected opportunity for skill matching
    target_opp = None
    if selected_opp_id:
        target_opp = Opportunity.query.get(selected_opp_id)
    elif opps:
        target_opp = opps[0]

    # Query all students
    query = StudentProfile.query
    if search_name:
        query = query.filter(StudentProfile.name_display.ilike(f"%{search_name}%"))
    if min_cgpa:
        query = query.filter(StudentProfile.cgpa >= min_cgpa)
    if career_goal:
        query = query.filter(StudentProfile.career_goal == career_goal)

    students = query.all()
    candidate_cards = []

    for st in students:
        # Check skill filter if requested
        if skill_id:
            has_skill = st.skills.filter_by(skill_id=skill_id, is_verified=True).first()
            if not has_skill:
                continue

        # Compute skill compatibility for selected opportunity
        compatibility = 75
        if target_opp:
            match_res = calculate_skill_match(st, target_opp)
            compatibility = match_res['match_percentage']

        verified_skills_list = []
        for ss in st.skills:
            if ss.is_verified and ss.skill_ref:
                verified_skills_list.append({
                    'name': ss.skill_ref.name,
                    'score': ss.verified_score
                })

        candidate_cards.append({
            'student': st,
            'compatibility': compatibility,
            'verified_skills': verified_skills_list,
            'projects_count': st.projects.count(),
            'has_resume': bool(st.resume_file_path)
        })

    # Sort candidates by compatibility descending
    candidate_cards.sort(key=lambda x: x['compatibility'], reverse=True)

    career_goals = [
        "Software Developer", "Data Scientist", "Web Developer",
        "AI/ML Engineer", "Cloud Engineer", "Data Analyst",
        "Mobile App Developer", "DevOps Engineer"
    ]

    return render_template(
        'industry/candidates.html',
        company=company,
        opps=opps,
        target_opp=target_opp,
        candidate_cards=candidate_cards,
        all_skills=all_skills,
        career_goals=career_goals,
        selected_opp_id=target_opp.id if target_opp else None,
        search_name=search_name,
        min_cgpa=min_cgpa,
        selected_career_goal=career_goal
    )


@industry_bp.route('/api/candidate/<int:student_id>')
@role_required('industry')
def candidate_profile(student_id):
    company = get_current_industry()
    student = StudentProfile.query.get_or_404(student_id)

    # Trigger profile view notification with 24-hr deduplication
    record_profile_view(company.user_id, student)

    # Opportunity compatibility
    opp_id = request.args.get('opp_id', type=int)
    compatibility = None
    why_match = []
    if opp_id:
        opp = Opportunity.query.get(opp_id)
        if opp:
            m = calculate_skill_match(student, opp)
            compatibility = m['match_percentage']
            why_match = m['why_match']

    skills_data = []
    for ss in student.skills:
        if ss.skill_ref:
            skills_data.append({
                'name': ss.skill_ref.name,
                'score': ss.verified_score,
                'is_verified': ss.is_verified,
                'category': ss.skill_ref.category
            })

    projects_data = [{
        'title': p.title,
        'description': p.description,
        'technologies': p.technologies,
        'role': p.role,
        'project_url': p.project_url
    } for p in student.projects]

    certs_data = [{
        'name': c.name,
        'issuing_org': c.issuing_org,
        'issue_date': c.issue_date,
        'credential_url': c.credential_url
    } for c in student.certifications]

    exp_data = [{
        'company': e.company,
        'role': e.role,
        'duration': e.duration,
        'description': e.description
    } for e in student.experiences]

    return jsonify({
        'id': student.id,
        'name_display': student.name_display,
        'college': student.college,
        'branch': student.branch,
        'year': student.year,
        'cgpa': student.cgpa,
        'bio': student.bio,
        'career_goal': student.career_goal,
        'interested_domains': student.interested_domains,
        'skills': skills_data,
        'projects': projects_data,
        'certifications': certs_data,
        'experiences': exp_data,
        'has_resume': bool(student.resume_file_path),
        'resume_url': url_for('static', filename='../' + student.resume_file_path) if student.resume_file_path else None,
        'github_url': student.github_url,
        'linkedin_url': student.linkedin_url,
        'portfolio_url': student.portfolio_url,
        'compatibility': compatibility,
        'why_match': why_match
    })


# -----------------------------------------------------------------------------
# 4. APPLICATIONS & RECRUITMENT MANAGEMENT
# -----------------------------------------------------------------------------
@industry_bp.route('/applications')
@role_required('industry')
def applications():
    company = get_current_industry()
    opps = company.opportunities.all()

    # Query all applications for this company's opportunities
    opp_ids = [o.id for o in opps]
    query = Application.query.filter(
        (Application.company_id == company.id) | (Application.opportunity_id.in_(opp_ids))
    )

    # Filter by opportunity
    filter_opp_id = request.args.get('opp_id', type=int)
    if filter_opp_id:
        query = query.filter_by(opportunity_id=filter_opp_id)

    # Filter by status
    filter_status = request.args.get('status', '').strip()
    if filter_status:
        query = query.filter_by(status=filter_status)

    apps_list = query.order_by(Application.submitted_date.desc()).all()

    # Status count badges
    counts = {
        'all': len(apps_list),
        'Applied': sum(1 for a in apps_list if a.status == 'Applied'),
        'Under Review': sum(1 for a in apps_list if a.status == 'Under Review'),
        'Shortlisted': sum(1 for a in apps_list if a.status == 'Shortlisted'),
        'Interview': sum(1 for a in apps_list if a.status == 'Interview'),
        'Selected': sum(1 for a in apps_list if a.status == 'Selected'),
        'Rejected': sum(1 for a in apps_list if a.status == 'Rejected')
    }

    return render_template(
        'industry/applications.html',
        company=company,
        opps=opps,
        applications=apps_list,
        counts=counts,
        active_opp_id=filter_opp_id,
        active_status=filter_status
    )


@industry_bp.route('/applications/<int:id>/status', methods=['POST'])
@role_required('industry')
def update_application_status(id):
    company = get_current_industry()
    app_record = Application.query.filter_by(id=id, company_id=company.id).first_or_404()
    new_status = request.form.get('status')

    valid_statuses = ['Under Review', 'Shortlisted', 'Interview', 'Selected', 'Rejected']
    if new_status not in valid_statuses:
        flash('Invalid status transition.', 'danger')
        return redirect(url_for('industry.applications'))

    status_order = {
        'Applied': 0,
        'Under Review': 1,
        'Shortlisted': 2,
        'Interview': 3,
        'Selected': 4,
        'Rejected': 4
    }
    if status_order.get(new_status, -1) <= status_order.get(app_record.status, -1):
        flash('Applications can only move forward through the recruitment pipeline.', 'warning')
        return redirect(url_for('industry.applications'))

    app_record.status = new_status
    app_record.status_updated_date = datetime.utcnow()

    # Create Student Notification based on new status
    opp_title = app_record.opportunity.title if app_record.opportunity else "Role"
    company_name = company.company_name

    msg_map = {
        'Under Review': f"Your application for {company_name} - {opp_title} is now under active review.",
        'Shortlisted': f"Great news! You have been shortlisted for {company_name} - {opp_title}. The hiring team will contact you shortly.",
        'Interview': f"You have an interview scheduled for {company_name} - {opp_title}. Check your registered communication details.",
        'Selected': f"Congratulations! You have been selected for {company_name} - {opp_title}!",
        'Rejected': f"Status update: The position for {company_name} - {opp_title} has been filled. Keep improving your skills and apply to new roles!"
    }

    create_notification(
        user_id=app_record.student.user_id,
        event_type="status_changed",
        message=msg_map.get(new_status, f"Application status updated to {new_status}."),
        related_id=app_record.id
    )

    db.session.commit()
    flash(f"Candidate application status updated to '{new_status}'.", 'success')
    return redirect(url_for('industry.applications'))


# -----------------------------------------------------------------------------
# 5. NOTIFICATIONS
# -----------------------------------------------------------------------------
@industry_bp.route('/notifications')
@role_required('industry')
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    return render_template(
        'industry/notifications.html',
        notifications=notifs,
        unread_count=unread_count
    )
