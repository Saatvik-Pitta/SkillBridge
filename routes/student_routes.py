import os
import random
from datetime import datetime, timedelta
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    jsonify, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from models import (
    db, StudentProfile, StudentProject, StudentCertification,
    StudentAchievement, StudentExperience, Skill, StudentSkill,
    Assessment, AssessmentQuestion, AssessmentAttempt, Opportunity,
    Application, LearningResource, Notification, CareerRequirement
)
from auth import role_required, get_current_user
from helpers import (
    calculate_skill_match, calculate_skill_gaps,
    calculate_career_readiness, get_personalized_learning,
    create_notification
)

student_bp = Blueprint('student', __name__, url_prefix='/student')

def get_current_student():
    user = get_current_user()
    if user and user.role == 'student':
        if not user.student_profile:
            profile = StudentProfile(user_id=user.id, name_display="Student 123")
            db.session.add(profile)
            db.session.commit()
        return user.student_profile
    return None


# -----------------------------------------------------------------------------
# 1. PROFILE & SUB-RECORDS
# -----------------------------------------------------------------------------
@student_bp.route('/profile')
@role_required('student')
def profile():
    student = get_current_student()
    
    # Calculate Profile Summary
    verified_skills_count = student.skills.filter_by(is_verified=True).count()
    projects_count = student.projects.count()
    certs_count = student.certifications.count()
    has_resume = bool(student.resume_file_path)
    
    # Completeness calculation
    completeness = 40
    if student.bio: completeness += 10
    if verified_skills_count >= 3: completeness += 20
    if projects_count >= 1: completeness += 15
    if has_resume: completeness += 15
    completeness = min(100, completeness)

    # Fetch technical and soft skills
    tech_skills = []
    soft_skills = []
    
    for ss in student.skills:
        if ss.skill_ref:
            skill_info = {
                'id': ss.id,
                'skill_id': ss.skill_id,
                'name': ss.skill_ref.name,
                'category': ss.skill_ref.category,
                'verified_score': ss.verified_score,
                'is_verified': ss.is_verified,
                'verified_date': ss.verified_date.strftime('%b %d, %Y') if ss.verified_date else None
            }
            if ss.skill_ref.category == 'technical':
                tech_skills.append(skill_info)
            else:
                soft_skills.append(skill_info)

    available_career_goals = [
        "Software Developer", "Data Scientist", "Web Developer",
        "AI/ML Engineer", "Cloud Engineer", "Data Analyst",
        "Mobile App Developer", "DevOps Engineer"
    ]

    all_domains = [
        "AI/ML", "Data Science", "Data Analytics", "Web Development",
        "Mobile App Development", "Cybersecurity", "Cloud Computing",
        "Software Development", "IoT", "Blockchain", "DevOps"
    ]

    return render_template(
        'student/profile.html',
        student=student,
        summary={
            'verified_skills_count': verified_skills_count,
            'projects_count': projects_count,
            'certs_count': certs_count,
            'has_resume': has_resume,
            'completeness': completeness
        },
        tech_skills=tech_skills,
        soft_skills=soft_skills,
        available_career_goals=available_career_goals,
        all_domains=all_domains
    )


@student_bp.route('/profile/update', methods=['POST'])
@role_required('student')
def update_profile():
    student = get_current_student()
    
    # Basic Info
    college = request.form.get('college', '').strip()
    branch = request.form.get('branch', '').strip()
    year = request.form.get('year', '').strip()
    bio = request.form.get('bio', '').strip()
    cgpa_str = request.form.get('cgpa', '3.8')
    career_goal = request.form.get('career_goal', 'Software Developer')
    domains = request.form.getlist('domains')
    
    # Links
    github_url = request.form.get('github_url', '').strip()
    linkedin_url = request.form.get('linkedin_url', '').strip()
    portfolio_url = request.form.get('portfolio_url', '').strip()

    # Validation
    try:
        cgpa = float(cgpa_str)
        if not (0.0 <= cgpa <= 4.0):
            flash('CGPA must be a valid number between 0.0 and 4.0', 'danger')
            return redirect(url_for('student.profile'))
    except ValueError:
        flash('Invalid CGPA format.', 'danger')
        return redirect(url_for('student.profile'))

    if len(domains) > 3:
        flash('Maximum 3 interested domains allowed.', 'danger')
        return redirect(url_for('student.profile'))

    student.college = college or student.college
    student.branch = branch or student.branch
    student.year = year or student.year
    student.cgpa = cgpa
    student.bio = bio[:500]
    student.career_goal = career_goal
    student.interested_domains = domains
    student.github_url = github_url
    student.linkedin_url = linkedin_url
    student.portfolio_url = portfolio_url

    db.session.commit()
    flash('Profile updated successfully! Career recommendations have refreshed.', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/projects/add', methods=['POST'])
@role_required('student')
def add_project():
    student = get_current_student()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    technologies = request.form.get('technologies', '').strip()
    role = request.form.get('role', 'Developer').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    project_url = request.form.get('project_url', '').strip()

    if not title or not description or not technologies:
        flash('Title, description, and technologies are required.', 'danger')
        return redirect(url_for('student.profile'))

    project = StudentProject(
        student_id=student.id,
        title=title,
        description=description[:500],
        technologies=technologies,
        role=role,
        start_date=start_date,
        end_date=end_date,
        project_url=project_url
    )
    db.session.add(project)
    db.session.commit()
    flash('Project added successfully.', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/projects/<int:id>/delete', methods=['POST'])
@role_required('student')
def delete_project(id):
    student = get_current_student()
    project = StudentProject.query.filter_by(id=id, student_id=student.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/certifications/add', methods=['POST'])
@role_required('student')
def add_certification():
    student = get_current_student()
    name = request.form.get('name', '').strip()
    issuing_org = request.form.get('issuing_org', '').strip()
    issue_date = request.form.get('issue_date', '').strip()
    credential_url = request.form.get('credential_url', '').strip()

    if not name or not issuing_org:
        flash('Certification name and issuing organization are required.', 'danger')
        return redirect(url_for('student.profile'))

    cert = StudentCertification(
        student_id=student.id,
        name=name,
        issuing_org=issuing_org,
        issue_date=issue_date,
        credential_url=credential_url
    )
    db.session.add(cert)
    db.session.commit()
    flash('Certification added.', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/certifications/<int:id>/delete', methods=['POST'])
@role_required('student')
def delete_certification(id):
    student = get_current_student()
    cert = StudentCertification.query.filter_by(id=id, student_id=student.id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    flash('Certification removed.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/achievements/add', methods=['POST'])
@role_required('student')
def add_achievement():
    student = get_current_student()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    date_achieved = request.form.get('date_achieved', '').strip()

    if not title or not description:
        flash('Achievement title and description are required.', 'danger')
        return redirect(url_for('student.profile'))

    ach = StudentAchievement(
        student_id=student.id,
        title=title,
        description=description[:300],
        date_achieved=date_achieved
    )
    db.session.add(ach)
    db.session.commit()
    flash('Achievement added.', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/achievements/<int:id>/delete', methods=['POST'])
@role_required('student')
def delete_achievement(id):
    student = get_current_student()
    ach = StudentAchievement.query.filter_by(id=id, student_id=student.id).first_or_404()
    db.session.delete(ach)
    db.session.commit()
    flash('Achievement deleted.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/experiences/add', methods=['POST'])
@role_required('student')
def add_experience():
    student = get_current_student()
    company = request.form.get('company', '').strip()
    role = request.form.get('role', '').strip()
    duration = request.form.get('duration', '').strip()
    description = request.form.get('description', '').strip()
    skills_used = request.form.get('skills_used', '').strip()

    if not company or not role or not duration:
        flash('Company, role, and duration are required.', 'danger')
        return redirect(url_for('student.profile'))

    exp = StudentExperience(
        student_id=student.id,
        company=company,
        role=role,
        duration=duration,
        description=description[:500],
        skills_used=skills_used
    )
    db.session.add(exp)
    db.session.commit()
    flash('Experience record added.', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/experiences/<int:id>/delete', methods=['POST'])
@role_required('student')
def delete_experience(id):
    student = get_current_student()
    exp = StudentExperience.query.filter_by(id=id, student_id=student.id).first_or_404()
    db.session.delete(exp)
    db.session.commit()
    flash('Experience record deleted.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/resume/upload', methods=['POST'])
@role_required('student')
def upload_resume():
    student = get_current_student()
    if 'resume_file' not in request.files:
        flash('No resume file provided.', 'danger')
        return redirect(url_for('student.profile'))

    file = request.files['resume_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('student.profile'))

    if file and file.filename.lower().endswith('.pdf'):
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(student.user_id))
        os.makedirs(user_dir, exist_ok=True)

        filename = f"resume_{int(datetime.utcnow().timestamp())}.pdf"
        file_path = os.path.join(user_dir, filename)
        file.save(file_path)

        relative_path = f"resumes/{student.user_id}/{filename}"
        student.resume_file_path = relative_path
        db.session.commit()

        flash('Resume PDF uploaded and verified successfully.', 'success')
    else:
        flash('Invalid file format. Only PDF resumes (< 5MB) are accepted.', 'danger')

    return redirect(url_for('student.profile'))


@student_bp.route('/resume/delete', methods=['POST'])
@role_required('student')
def delete_resume():
    student = get_current_student()
    student.resume_file_path = None
    db.session.commit()
    flash('Resume removed from profile.', 'info')
    return redirect(url_for('student.profile'))


# -----------------------------------------------------------------------------
# 2. SKILL GAP & CAREER READINESS
# -----------------------------------------------------------------------------
@student_bp.route('/skill-gap')
@role_required('student')
def skill_gap():
    student = get_current_student()
    gaps_info = calculate_skill_gaps(student)
    readiness_info = calculate_career_readiness(student)

    return render_template(
        'student/skill_gap.html',
        student=student,
        gaps=gaps_info,
        readiness=readiness_info
    )


# -----------------------------------------------------------------------------
# 3. PERSONALIZED LEARNING
# -----------------------------------------------------------------------------
@student_bp.route('/learning')
@role_required('student')
def learning():
    student = get_current_student()
    personalized_resources = get_personalized_learning(student)
    
    # Filter parameters
    search_query = request.args.get('search', '').strip().lower()
    skill_filter = request.args.get('skill', '').strip()
    category_filter = request.args.get('category', '').strip()
    difficulty_filter = request.args.get('difficulty', '').strip()

    filtered = []
    for r in personalized_resources:
        if search_query:
            if search_query not in r.title.lower() and search_query not in r.description.lower():
                continue
        if skill_filter:
            if not r.skill or skill_filter.lower() != r.skill.name.lower():
                continue
        if category_filter:
            if category_filter.lower() != r.category.lower():
                continue
        if difficulty_filter:
            if difficulty_filter.lower() != r.difficulty.lower():
                continue
        filtered.append(r)

    # Categories and skills for filters
    all_skills = Skill.query.order_by(Skill.name).all()
    categories = sorted(list(set(r.category for r in personalized_resources)))

    # High priority recommendations (top 4)
    top_recommended = personalized_resources[:4]

    return render_template(
        'student/learning.html',
        student=student,
        top_recommended=top_recommended,
        resources=filtered,
        all_skills=all_skills,
        categories=categories,
        active_skill=skill_filter,
        active_category=category_filter,
        active_difficulty=difficulty_filter,
        search_query=search_query,
        total_count=len(filtered)
    )


# -----------------------------------------------------------------------------
# 4. APPLICATIONS & OPPORTUNITIES DISCOVERY
# -----------------------------------------------------------------------------
@student_bp.route('/applications')
@role_required('student')
def applications():
    student = get_current_student()
    
    # Active & past applications
    apps = student.applications.order_by(Application.submitted_date.desc()).all()
    active_apps = [a for a in apps if a.status not in ['Selected', 'Rejected']]
    history_apps = [a for a in apps if a.status in ['Selected', 'Rejected']]

    # Browse opportunities
    opportunities = Opportunity.query.filter_by(status='published').order_by(Opportunity.created_at.desc()).all()
    
    # Precompute match scores
    opps_with_scores = []
    for opp in opportunities:
        match_info = calculate_skill_match(student, opp)
        has_applied = any(a.opportunity_id == opp.id for a in apps)
        opps_with_scores.append({
            'opp': opp,
            'match_info': match_info,
            'has_applied': has_applied
        })

    # Sort opportunities: by best skill match descending
    sort_by = request.args.get('sort', 'match')
    if sort_by == 'match':
        opps_with_scores.sort(key=lambda x: x['match_info']['match_percentage'], reverse=True)
    elif sort_by == 'deadline':
        opps_with_scores.sort(key=lambda x: x['opp'].deadline)

    return render_template(
        'student/applications.html',
        student=student,
        active_apps=active_apps,
        history_apps=history_apps,
        opportunities=opps_with_scores,
        sort_by=sort_by
    )


@student_bp.route('/api/opportunity/<int:id>/details')
@role_required('student')
def opportunity_details(id):
    student = get_current_student()
    opp = Opportunity.query.get_or_404(id)
    match_info = calculate_skill_match(student, opp)
    
    # Check if already applied
    existing_app = Application.query.filter_by(student_id=student.id, opportunity_id=opp.id).first()

    return jsonify({
        'id': opp.id,
        'company_name': opp.company_name,
        'title': opp.title,
        'description': opp.description,
        'opportunity_type': opp.opportunity_type.capitalize(),
        'location': opp.location,
        'work_mode': opp.work_mode,
        'duration': opp.duration,
        'experience_level': opp.experience_level,
        'eligibility': opp.eligibility,
        'deadline': opp.deadline,
        'stipend_salary': opp.stipend_salary or 'Not specified',
        'required_skills': opp.required_skills,
        'required_skill_levels': opp.required_skill_levels,
        'application_questions': opp.application_questions,
        'source_url': opp.source_url,
        'date_retrieved': opp.date_retrieved,
        'match_percentage': match_info['match_percentage'],
        'matching_skills': match_info['matching_skills'],
        'gap_skills': match_info['gap_skills'],
        'why_match': match_info['why_match'],
        'has_applied': existing_app is not None,
        'has_stored_resume': bool(student.resume_file_path),
        'stored_resume_path': student.resume_file_path or ''
    })


@student_bp.route('/applications/apply/<int:opportunity_id>', methods=['POST'])
@role_required('student')
def apply_opportunity(opportunity_id):
    student = get_current_student()
    opp = Opportunity.query.get_or_404(opportunity_id)

    # 1. Duplicate prevention
    existing = Application.query.filter_by(student_id=student.id, opportunity_id=opp.id).first()
    if existing:
        flash('You have already submitted an application for this opportunity.', 'warning')
        return redirect(url_for('student.applications'))

    # 2. Resume selection or upload
    resume_choice = request.form.get('resume_choice', 'stored')
    final_resume_path = student.resume_file_path

    if resume_choice == 'new':
        if 'new_resume_file' in request.files and request.files['new_resume_file'].filename:
            file = request.files['new_resume_file']
            if file.filename.lower().endswith('.pdf'):
                user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(student.user_id))
                os.makedirs(user_dir, exist_ok=True)
                filename = f"resume_{int(datetime.utcnow().timestamp())}.pdf"
                file.save(os.path.join(user_dir, filename))
                final_resume_path = f"resumes/{student.user_id}/{filename}"
                student.resume_file_path = final_resume_path
                db.session.commit()
            else:
                flash('Resume must be a PDF file.', 'danger')
                return redirect(url_for('student.applications'))

    if not final_resume_path:
        flash('A valid resume is required to submit your application.', 'danger')
        return redirect(url_for('student.applications'))

    # 3. Application Questions Answers
    answers = []
    for q in opp.application_questions:
        q_id = q.get('id')
        q_text = q.get('question_text')
        ans_text = request.form.get(f"question_{q_id}", "").strip()
        if q.get('is_required') and not ans_text:
            flash(f"Please answer the required question: {q_text}", 'danger')
            return redirect(url_for('student.applications'))
        answers.append({
            'question_id': q_id,
            'question_text': q_text,
            'answer': ans_text
        })

    # 4. Calculate skill match at application time
    match_info = calculate_skill_match(student, opp)

    # 5. Create Application record
    app_record = Application(
        student_id=student.id,
        opportunity_id=opp.id,
        company_id=opp.company_id,
        resume_file_path=final_resume_path,
        status="Applied",
        skill_match_score=match_info['match_percentage']
    )
    app_record.answers_to_questions = answers
    db.session.add(app_record)
    db.session.flush()

    # 6. Create Student Notification
    create_notification(
        user_id=student.user_id,
        event_type="application_submitted",
        message=f"Your application for {opp.title} at {opp.company_name} has been submitted successfully.",
        related_id=app_record.id
    )

    # 7. Create Industry Notification if opportunity belongs to an industry partner
    if opp.company and opp.company.user_id:
        create_notification(
            user_id=opp.company.user_id,
            event_type="new_application",
            message=f"New candidate application received for '{opp.title}' from {student.name_display}.",
            related_id=app_record.id
        )

    db.session.commit()
    flash(f"Application for '{opp.title}' submitted successfully!", 'success')
    return redirect(url_for('student.applications'))


# -----------------------------------------------------------------------------
# 5. NOTIFICATIONS
# -----------------------------------------------------------------------------
@student_bp.route('/notifications')
@role_required('student')
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    return render_template(
        'student/notifications.html',
        notifications=notifs,
        unread_count=unread_count
    )


@student_bp.route('/notifications/<int:id>/read', methods=['POST'])
@role_required('student')
def mark_notification_read(id):
    user = get_current_user()
    notif = Notification.query.filter_by(id=id, user_id=user.id).first_or_404()
    notif.read = True
    db.session.commit()
    return jsonify({'success': True})


@student_bp.route('/notifications/read-all', methods=['POST'])
@role_required('student')
def mark_all_notifications_read():
    user = get_current_user()
    Notification.query.filter_by(user_id=user.id, read=False).update({'read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('student.notifications'))


@student_bp.route('/notifications/<int:id>/delete', methods=['POST'])
@role_required('student')
def delete_notification(id):
    user = get_current_user()
    notif = Notification.query.filter_by(id=id, user_id=user.id).first_or_404()
    db.session.delete(notif)
    db.session.commit()
    flash('Notification deleted.', 'info')
    return redirect(url_for('student.notifications'))


# -----------------------------------------------------------------------------
# 6. ASSESSMENTS ENGINE
# -----------------------------------------------------------------------------
@student_bp.route('/assessment/<int:skill_id>')
@role_required('student')
def take_assessment(skill_id):
    student = get_current_student()
    skill = Skill.query.get_or_404(skill_id)
    assessment = Assessment.query.filter_by(skill_id=skill.id).first()

    if not assessment or assessment.questions.count() == 0:
        flash(f"Assessment for {skill.name} is currently undergoing syllabus updates.", 'warning')
        return redirect(url_for('student.skill_gap'))

    # Retake Rule: 5 days cooldown
    last_attempt = AssessmentAttempt.query.filter_by(
        student_id=student.id,
        assessment_id=assessment.id
    ).order_by(AssessmentAttempt.submitted_date.desc()).first()

    if last_attempt and last_attempt.next_retake_date > datetime.utcnow():
        delta = last_attempt.next_retake_date - datetime.utcnow()
        days_left = max(1, delta.days + 1)
        flash(f"Retake restricted: You can retake the {skill.name} assessment in {days_left} day(s).", 'warning')
        return redirect(url_for('student.skill_gap'))

    # Randomize questions: pick 6-8 questions
    all_questions = assessment.questions.all()
    num_to_pick = min(len(all_questions), 8)
    selected_questions = random.sample(all_questions, num_to_pick)

    # Randomize answer options order while tracking the correct index
    questions_data = []
    for q in selected_questions:
        indexed_opts = list(enumerate(q.options))
        random.shuffle(indexed_opts)
        
        shuffled_options = [opt[1] for opt in indexed_opts]
        # Find where original correct_option_index moved to
        new_correct_idx = next(i for i, opt in enumerate(indexed_opts) if opt[0] == q.correct_option_index)

        questions_data.append({
            'id': q.id,
            'question_text': q.question_text,
            'options': shuffled_options,
            'correct_index': new_correct_idx, # Kept on backend session only
            'explanation': q.explanation,
            'topic': q.topic
        })

    # Prepare safe data for frontend (NEVER send correct_index or explanation)
    client_questions = [{
        'id': q['id'],
        'question_text': q['question_text'],
        'options': q['options'],
        'topic': q['topic']
    } for q in questions_data]

    return render_template(
        'student/assessment.html',
        student=student,
        skill=skill,
        assessment=assessment,
        questions=client_questions,
        questions_json=client_questions,
        server_eval_data=[{'id': q['id'], 'correct_index': q['correct_index'], 'explanation': q['explanation'], 'topic': q['topic']} for q in questions_data]
    )


@student_bp.route('/assessment/submit', methods=['POST'])
@role_required('student')
def submit_assessment():
    student = get_current_student()
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid submission payload.'}), 400

    assessment_id = data.get('assessment_id')
    eval_data = data.get('eval_data', [])
    user_answers = data.get('answers', {})  # map: question_id -> chosen option index

    assessment = Assessment.query.get_or_404(assessment_id)

    # Calculate score
    correct_count = 0
    total_questions = len(eval_data)
    topic_stats = {}
    detailed_answers = []

    for q in eval_data:
        qid_str = str(q['id'])
        chosen_idx = user_answers.get(qid_str)
        is_correct = (chosen_idx is not None and chosen_idx == q['correct_index'])
        if is_correct:
            correct_count += 1

        topic = q.get('topic', 'General')
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if is_correct:
            topic_stats[topic]['correct'] += 1

        detailed_answers.append({
            'question_id': q['id'],
            'chosen_index': chosen_idx,
            'correct_index': q['correct_index'],
            'is_correct': is_correct,
            'explanation': q['explanation'],
            'topic': topic
        })

    percentage = int(round((correct_count / total_questions) * 100)) if total_questions > 0 else 0
    next_retake = datetime.utcnow() + timedelta(days=5)

    # Save attempt
    attempt = AssessmentAttempt(
        student_id=student.id,
        assessment_id=assessment.id,
        score=correct_count,
        total_questions=total_questions,
        percentage=percentage,
        submitted_date=datetime.utcnow(),
        next_retake_date=next_retake
    )
    attempt.answers = detailed_answers
    attempt.topic_breakdown = topic_stats
    db.session.add(attempt)

    # Update StudentSkills record (Keep HIGHER score rule)
    ss = StudentSkill.query.filter_by(student_id=student.id, skill_id=assessment.skill_id).first()
    if not ss:
        ss = StudentSkill(student_id=student.id, skill_id=assessment.skill_id)
        db.session.add(ss)

    if ss.verified_score is None or percentage > ss.verified_score:
        ss.verified_score = percentage

    ss.is_verified = True
    ss.verified_date = datetime.utcnow()

    # Create verification notification
    create_notification(
        user_id=student.user_id,
        event_type="assessment_result",
        message=f"Assessment submitted for {assessment.skill.name}: You scored {percentage}% ({correct_count}/{total_questions}). Verified skill badge updated!",
        related_id=attempt.id
    )

    db.session.commit()

    return jsonify({
        'success': True,
        'attempt_id': attempt.id,
        'redirect_url': url_for('student.assessment_result', attempt_id=attempt.id)
    })


@student_bp.route('/assessment/result/<int:attempt_id>')
@role_required('student')
def assessment_result(attempt_id):
    student = get_current_student()
    attempt = AssessmentAttempt.query.filter_by(id=attempt_id, student_id=student.id).first_or_404()
    assessment = attempt.assessment

    # Check retake eligibility
    retake_eligible = datetime.utcnow() >= attempt.next_retake_date
    days_to_retake = max(0, (attempt.next_retake_date - datetime.utcnow()).days + 1)

    return render_template(
        'student/assessment_result.html',
        student=student,
        attempt=attempt,
        assessment=assessment,
        retake_eligible=retake_eligible,
        days_to_retake=days_to_retake
    )


@student_bp.route('/assessment/history')
@role_required('student')
def assessment_history():
    student = get_current_student()
    attempts = student.attempts.order_by(AssessmentAttempt.submitted_date.desc()).all()
    
    # Progress map per skill
    history_by_skill = {}
    for att in attempts:
        sname = att.assessment.skill.name if att.assessment and att.assessment.skill else "Skill"
        if sname not in history_by_skill:
            history_by_skill[sname] = []
        history_by_skill[sname].append({
            'date': att.submitted_date.strftime('%b %d'),
            'score': att.percentage
        })

    return render_template(
        'student/history.html',
        student=student,
        attempts=attempts,
        history_by_skill=history_by_skill
    )
