from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from models import (
    db, AcademicianProfile, Collaboration, Notification, IndustryProfile,
    InstitutionProfile
)
from auth import role_required, get_current_user
from helpers import create_notification

academician_bp = Blueprint('academician', __name__, url_prefix='/academician')

def get_current_academician():
    user = get_current_user()
    if user and user.role == 'academician':
        if not user.academician_profile:
            profile = AcademicianProfile(user_id=user.id, name_display="Dr. A. Sharma")
            db.session.add(profile)
            db.session.commit()
        return user.academician_profile
    return None


# -----------------------------------------------------------------------------
# 1. FACULTY PROFILE
# -----------------------------------------------------------------------------
@academician_bp.route('/profile')
@role_required('academician')
def profile():
    faculty = get_current_academician()
    
    collabs_count = faculty.collaborations.count()
    active_collabs = faculty.collaborations.filter_by(status='Active').count()

    return render_template(
        'academician/profile.html',
        faculty=faculty,
        collabs_count=collabs_count,
        active_collabs=active_collabs
    )


@academician_bp.route('/profile/update', methods=['POST'])
@role_required('academician')
def update_profile():
    faculty = get_current_academician()
    
    faculty.name_display = request.form.get('name_display', faculty.name_display).strip()
    faculty.institution = request.form.get('institution', faculty.institution).strip()
    faculty.department = request.form.get('department', faculty.department).strip()
    faculty.designation = request.form.get('designation', faculty.designation).strip()
    try:
        faculty.experience_years = int(request.form.get('experience_years', faculty.experience_years))
    except ValueError:
        pass
    
    expertise_str = request.form.get('expertise_areas', '')
    if expertise_str:
        faculty.expertise_areas = [x.strip() for x in expertise_str.split(',') if x.strip()]

    research_str = request.form.get('research_interests', '')
    if research_str:
        faculty.research_interests = [x.strip() for x in research_str.split(',') if x.strip()]

    faculty.linkedin_url = request.form.get('linkedin_url', faculty.linkedin_url).strip()
    faculty.website_url = request.form.get('website_url', faculty.website_url).strip()

    db.session.commit()
    flash('Faculty profile updated successfully.', 'success')
    return redirect(url_for('academician.profile'))


# -----------------------------------------------------------------------------
# 2. FACULTY OPPORTUNITIES (FDP, RESEARCH, WORKSHOPS)
# -----------------------------------------------------------------------------
@academician_bp.route('/opportunities')
@role_required('academician')
def opportunities():
    faculty = get_current_academician()

    # Curated real-world faculty development & academic collaboration programs
    faculty_opps = [
        {
            'id': 1,
            'title': 'AI/ML Faculty Development Program (FDP)',
            'organization': 'Amazon Web Services & AICTE',
            'type': 'FDP',
            'dates': 'Oct 15 - Oct 20, 2026',
            'location': 'Virtual / Online',
            'eligibility': 'Faculty & Researchers in Engineering/Science',
            'deadline': '2026-10-05',
            'description': 'Hands-on 5-day pedagogy workshop on deploying deep learning models on AWS SageMaker and integrating cloud labs into undergraduate curricula.',
            'status': 'Open'
        },
        {
            'id': 2,
            'title': 'Industry Sabbatical & Research Residency',
            'organization': 'Demo Tech Solutions',
            'type': 'Research Collaboration',
            'dates': 'Spring Semester 2027',
            'location': 'Hyderabad / Hybrid',
            'eligibility': 'Assistant / Associate Professors',
            'deadline': '2026-11-10',
            'description': 'Collaborative research residency in distributed cache optimization with cloud software architects. Includes research fellowship grant.',
            'status': 'Open'
        },
        {
            'id': 3,
            'title': 'Senior Guest Lecturer in High Performance Computing',
            'organization': 'NASSCOM FutureSkills Prime',
            'type': 'Guest Lecturer Role',
            'dates': 'Flexible (2 weekends)',
            'location': 'Hybrid',
            'eligibility': 'PhD or 5+ years experience in Systems',
            'deadline': '2026-10-18',
            'description': 'Deliver interactive masterclasses for national student cohorts on GPU parallelism and CUDA programming architectures.',
            'status': 'Open'
        },
        {
            'id': 4,
            'title': 'Industry Consultancy: Zero-Trust Security Frameworks',
            'organization': 'CyberShield Systems',
            'type': 'Consultancy Project',
            'dates': '3 Months',
            'location': 'Remote',
            'eligibility': 'Faculty with publications in Network Security',
            'deadline': '2026-10-30',
            'description': 'Technical advisory role evaluating identity propagation protocols and micro-segmentation models for financial banking clients.',
            'status': 'Open'
        }
    ]

    opp_type_filter = request.args.get('type', '').strip()
    if opp_type_filter:
        faculty_opps = [o for o in faculty_opps if o['type'] == opp_type_filter]

    return render_template(
        'academician/opportunities.html',
        faculty=faculty,
        opportunities=faculty_opps,
        active_type=opp_type_filter
    )


@academician_bp.route('/opportunities/apply/<int:id>', methods=['POST'])
@role_required('academician')
def apply_opportunity(id):
    faculty = get_current_academician()
    program_name = request.form.get('program_name', 'Faculty Program')
    
    # Create notification for academician
    create_notification(
        user_id=faculty.user_id,
        event_type="fdp_registration_confirmed",
        message=f"Your expression of interest for '{program_name}' has been recorded. Coordination details will be emailed."
    )
    flash(f"Expression of interest submitted for '{program_name}'.", 'success')
    return redirect(url_for('academician.opportunities'))


# -----------------------------------------------------------------------------
# 3. COLLABORATION (DISCOVERY & MANAGEMENT)
# -----------------------------------------------------------------------------
@academician_bp.route('/collaboration')
@role_required('academician')
def collaboration():
    faculty = get_current_academician()
    
    # Active collaborations involving this faculty
    my_collaborations = faculty.collaborations.order_by(Collaboration.created_at.desc()).all()

    # Discoverable collaborations from industry partners
    all_collabs = Collaboration.query.order_by(Collaboration.created_at.desc()).all()

    collab_types = [
        "Guest Lecture Series", "Live Projects", "Workshops",
        "Research Collaboration", "Curriculum Development", "Industry Mentorship"
    ]

    return render_template(
        'academician/collaboration.html',
        faculty=faculty,
        my_collaborations=my_collaborations,
        all_collaborations=all_collabs,
        collab_types=collab_types
    )


@academician_bp.route('/collaboration/create', methods=['POST'])
@role_required('academician')
def create_collaboration():
    faculty = get_current_academician()
    title = request.form.get('title', '').strip()
    c_type = request.form.get('collaboration_type', 'Guest Lecture Series')
    description = request.form.get('description', '').strip()
    duration = request.form.get('duration', '1 Semester').strip()
    commitment = request.form.get('commitment', '2 hours/week').strip()
    skills_needed = request.form.get('skills_needed', '').strip()
    deliverables = request.form.get('deliverables', '').strip()

    if not title or not description:
        flash('Title and description are required.', 'danger')
        return redirect(url_for('academician.collaboration'))

    collab = Collaboration(
        academician_id=faculty.id,
        title=title,
        collaboration_type=c_type,
        description=description,
        duration=duration,
        commitment=commitment,
        skills_needed=skills_needed,
        deliverables=deliverables,
        status='Proposed'
    )
    db.session.add(collab)
    db.session.commit()

    flash('Collaboration proposal submitted successfully.', 'success')
    return redirect(url_for('academician.collaboration'))


@academician_bp.route('/collaboration/<int:id>/status', methods=['POST'])
@role_required('academician')
def update_collaboration_status(id):
    faculty = get_current_academician()
    collab = Collaboration.query.filter_by(id=id, academician_id=faculty.id).first_or_404()
    new_status = request.form.get('status')
    if new_status in ['Proposed', 'Accepted', 'Active', 'Completed']:
        collab.status = new_status
        db.session.commit()
        flash(f"Collaboration status updated to '{new_status}'.", 'info')
    return redirect(url_for('academician.collaboration'))


# -----------------------------------------------------------------------------
# 4. FACULTY LEARN & DEVELOPMENT
# -----------------------------------------------------------------------------
@academician_bp.route('/learn')
@role_required('academician')
def learn():
    faculty = get_current_academician()

    faculty_resources = [
        {
            'title': 'AI in Engineering Pedagogy & Assessment',
            'provider': 'NPTEL / IIT Madras',
            'category': 'Teaching Technology & Pedagogy',
            'duration': '4 Weeks',
            'url': 'https://nptel.ac.in',
            'description': 'Methods for structuring automated rubric evaluations, experiential project learning, and generative AI guidelines in university courses.'
        },
        {
            'title': 'Cloud Infrastructure Educator Program',
            'provider': 'Google Cloud for Education',
            'category': 'Industry Cloud Training',
            'duration': 'Self-Paced (6 Modules)',
            'url': 'https://cloud.google.com/edu',
            'description': 'Free instructor teaching resources, student sandbox access credits, and instructional slides for Kubernetes and BigQuery.'
        },
        {
            'title': 'Curriculum Alignment with NEP & Industry Standards',
            'provider': 'AICTE & National Board of Accreditation',
            'category': 'Curriculum Design',
            'duration': '2 Days',
            'url': 'https://aicte-india.org',
            'description': 'Frameworks for mapping course outcomes (COs) and program outcomes (POs) to emerging corporate industry skill benchmarks.'
        },
        {
            'title': 'Advanced Research Methodology & Grant Proposal Writing',
            'provider': 'DST / SERB India',
            'category': 'Research Development',
            'duration': '3 Weeks',
            'url': 'https://serb.gov.in',
            'description': 'Comprehensive guide to structuring international peer-reviewed journal papers and winning government-funded research grants.'
        }
    ]

    return render_template(
        'academician/learn.html',
        faculty=faculty,
        resources=faculty_resources
    )


# -----------------------------------------------------------------------------
# 5. NOTIFICATIONS
# -----------------------------------------------------------------------------
@academician_bp.route('/notifications')
@role_required('academician')
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=user.id, read=False).count()
    return render_template(
        'academician/notifications.html',
        notifications=notifs,
        unread_count=unread_count
    )
