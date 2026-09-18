import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # student, industry, academician, institution
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    industry_profile = db.relationship('IndustryProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    academician_profile = db.relationship('AcademicianProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    institution_profile = db.relationship('InstitutionProfile', backref='admin_user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    name_display = db.Column(db.String(100), nullable=False, default="Student 123")
    college = db.Column(db.String(150), default="Demo University")
    branch = db.Column(db.String(100), default="Computer Science")
    year = db.Column(db.String(50), default="2nd Year")
    cgpa = db.Column(db.Float, default=3.8)
    bio = db.Column(db.Text, default="Passionate about learning and building projects")
    career_goal = db.Column(db.String(100), default="Software Developer")
    _interested_domains = db.Column('interested_domains', db.Text, default='["Web Development", "AI/ML"]')
    resume_file_path = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True, default="https://github.com/student123-demo")
    linkedin_url = db.Column(db.String(255), nullable=True, default="https://linkedin.com/in/student123-demo")
    portfolio_url = db.Column(db.String(255), nullable=True, default="https://student123.dev")

    # Relationships
    skills = db.relationship('StudentSkill', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    projects = db.relationship('StudentProject', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    certifications = db.relationship('StudentCertification', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    achievements = db.relationship('StudentAchievement', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    experiences = db.relationship('StudentExperience', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    attempts = db.relationship('AssessmentAttempt', backref='student', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def interested_domains(self):
        if not self._interested_domains:
            return []
        try:
            return json.loads(self._interested_domains)
        except Exception:
            return []

    @interested_domains.setter
    def interested_domains(self, value):
        if isinstance(value, list):
            self._interested_domains = json.dumps(value[:3])
        else:
            self._interested_domains = '[]'


class StudentProject(db.Model):
    __tablename__ = 'student_projects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), default="Lead Developer")
    project_url = db.Column(db.String(255), nullable=True)


class StudentCertification(db.Model):
    __tablename__ = 'student_certifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    issuing_org = db.Column(db.String(150), nullable=False)
    issue_date = db.Column(db.String(50), nullable=True)
    credential_url = db.Column(db.String(255), nullable=True)


class StudentAchievement(db.Model):
    __tablename__ = 'student_achievements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_achieved = db.Column(db.String(50), nullable=True)


class StudentExperience(db.Model):
    __tablename__ = 'student_experiences'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_used = db.Column(db.String(255), nullable=True)


class IndustryProfile(db.Model):
    __tablename__ = 'industry_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False, default="Demo Tech Solutions")
    industry = db.Column(db.String(100), default="Technology")
    company_size = db.Column(db.String(50), default="250-1000")
    location = db.Column(db.String(150), default="Hyderabad, India")
    website = db.Column(db.String(255), default="https://demotech.example.com")
    description = db.Column(db.Text, default="Leading engineering solutions and intelligent digital platforms.")
    _hiring_interests = db.Column('hiring_interests', db.Text, default='["Internships", "Full-time"]')
    _commonly_required_skills = db.Column('commonly_required_skills', db.Text, default='["Python", "Data Structures", "SQL", "Git/GitHub"]')
    _collaboration_interests = db.Column('collaboration_interests', db.Text, default='["Guest Lectures", "Workshops", "Live Projects"]')

    opportunities = db.relationship('Opportunity', backref='company', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def hiring_interests(self):
        try:
            return json.loads(self._hiring_interests or '[]')
        except Exception:
            return []

    @hiring_interests.setter
    def hiring_interests(self, val):
        self._hiring_interests = json.dumps(val if isinstance(val, list) else [])

    @property
    def commonly_required_skills(self):
        try:
            return json.loads(self._commonly_required_skills or '[]')
        except Exception:
            return []

    @commonly_required_skills.setter
    def commonly_required_skills(self, val):
        self._commonly_required_skills = json.dumps(val if isinstance(val, list) else [])

    @property
    def collaboration_interests(self):
        try:
            return json.loads(self._collaboration_interests or '[]')
        except Exception:
            return []

    @collaboration_interests.setter
    def collaboration_interests(self, val):
        self._collaboration_interests = json.dumps(val if isinstance(val, list) else [])


class AcademicianProfile(db.Model):
    __tablename__ = 'academician_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    name_display = db.Column(db.String(100), default="Dr. A. Sharma")
    institution = db.Column(db.String(150), default="Demo University")
    department = db.Column(db.String(100), default="Computer Science")
    designation = db.Column(db.String(100), default="Assistant Professor")
    experience_years = db.Column(db.Integer, default=7)
    _expertise_areas = db.Column('expertise_areas', db.Text, default='["Machine Learning", "Algorithms", "Cloud Architecture"]')
    _research_interests = db.Column('research_interests', db.Text, default='["Applied GenAI", "Distributed Systems"]')
    linkedin_url = db.Column(db.String(255), nullable=True, default="https://linkedin.com/in/faculty-demo")
    website_url = db.Column(db.String(255), nullable=True, default="https://faculty.demouniversity.edu")

    collaborations = db.relationship('Collaboration', backref='academician', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def expertise_areas(self):
        try:
            return json.loads(self._expertise_areas or '[]')
        except Exception:
            return []

    @expertise_areas.setter
    def expertise_areas(self, val):
        self._expertise_areas = json.dumps(val if isinstance(val, list) else [])

    @property
    def research_interests(self):
        try:
            return json.loads(self._research_interests or '[]')
        except Exception:
            return []

    @research_interests.setter
    def research_interests(self, val):
        self._research_interests = json.dumps(val if isinstance(val, list) else [])


class InstitutionProfile(db.Model):
    __tablename__ = 'institution_profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, default="Demo University")
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    location = db.Column(db.String(150), default="Hyderabad, India")
    description = db.Column(db.Text, default="Premier academic institution committed to industry alignment.")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)  # technical, soft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assessments = db.relationship('Assessment', backref='skill', uselist=False, cascade="all, delete-orphan")
    learning_resources = db.relationship('LearningResource', backref='skill', lazy='dynamic', cascade="all, delete-orphan")
    student_skills = db.relationship('StudentSkill', backref='skill_ref', lazy='dynamic', cascade="all, delete-orphan")


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    verified_score = db.Column(db.Integer, nullable=True)  # 0-100 or null if not assessed
    self_rated_score = db.Column(db.Integer, nullable=True)
    verified_date = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('student_id', 'skill_id', name='uq_student_skill'),)


class CareerRequirement(db.Model):
    __tablename__ = 'career_requirements'
    id = db.Column(db.Integer, primary_key=True)
    career_goal = db.Column(db.String(100), unique=True, nullable=False)
    _required_skills = db.Column('required_skills', db.Text, nullable=False)
    _minimum_scores = db.Column('minimum_scores', db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def required_skills(self):
        try:
            return json.loads(self._required_skills or '[]')
        except Exception:
            return []

    @required_skills.setter
    def required_skills(self, val):
        self._required_skills = json.dumps(val if isinstance(val, list) else [])

    @property
    def minimum_scores(self):
        try:
            return json.loads(self._minimum_scores or '[]')
        except Exception:
            return []

    @minimum_scores.setter
    def minimum_scores(self, val):
        self._minimum_scores = json.dumps(val if isinstance(val, list) else [])


class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, unique=True)
    difficulty = db.Column(db.String(50), default="medium")
    title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, default="Answer all multiple choice questions. Retakes are permitted every 5 days.")
    time_limit_mins = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy='dynamic', cascade="all, delete-orphan")
    attempts = db.relationship('AssessmentAttempt', backref='assessment', lazy='dynamic', cascade="all, delete-orphan")


class AssessmentQuestion(db.Model):
    __tablename__ = 'assessment_questions'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    _options = db.Column('options', db.Text, nullable=False)  # JSON array of 4 options
    correct_option_index = db.Column(db.Integer, nullable=False)  # 0-3
    explanation = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), default="medium")
    topic = db.Column(db.String(100), default="General")

    @property
    def options(self):
        try:
            return json.loads(self._options or '[]')
        except Exception:
            return []

    @options.setter
    def options(self, val):
        self._options = json.dumps(val if isinstance(val, list) else [])


class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # raw score e.g. 6 out of 8
    total_questions = db.Column(db.Integer, nullable=False, default=8)
    percentage = db.Column(db.Integer, nullable=False)  # 0-100
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    _answers = db.Column('answers', db.Text, default='[]')  # JSON details of user choices
    _topic_breakdown = db.Column('topic_breakdown', db.Text, default='{}')
    next_retake_date = db.Column(db.DateTime, nullable=False)

    @property
    def answers(self):
        try:
            return json.loads(self._answers or '[]')
        except Exception:
            return []

    @answers.setter
    def answers(self, val):
        self._answers = json.dumps(val if isinstance(val, list) else [])

    @property
    def topic_breakdown(self):
        try:
            return json.loads(self._topic_breakdown or '{}')
        except Exception:
            return {}

    @topic_breakdown.setter
    def topic_breakdown(self, val):
        self._topic_breakdown = json.dumps(val if isinstance(val, dict) else {})


class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('industry_profiles.id', ondelete='CASCADE'), nullable=True)
    company_name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    opportunity_type = db.Column(db.String(50), nullable=False)  # internship, full-time, apprenticeship
    location = db.Column(db.String(150), nullable=False)
    work_mode = db.Column(db.String(50), default="Hybrid")  # remote, hybrid, on-site
    duration = db.Column(db.String(100), default="3 months")
    experience_level = db.Column(db.String(50), default="Fresher (0-1 years)")
    eligibility = db.Column(db.String(150), default="2nd-4th year students")
    deadline = db.Column(db.String(50), nullable=False)
    stipend_salary = db.Column(db.String(100), nullable=True)
    _required_skills = db.Column('required_skills', db.Text, nullable=False)  # JSON array
    _required_skill_levels = db.Column('required_skill_levels', db.Text, nullable=False)  # beginner/intermediate/advanced
    _application_questions = db.Column('application_questions', db.Text, default='[]')  # JSON array of questions
    source_url = db.Column(db.String(255), default="https://linkedin.com/jobs")
    date_retrieved = db.Column(db.String(50), default="Verified 2 days ago")
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default="published")  # published, draft, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='opportunity', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def required_skills(self):
        try:
            return json.loads(self._required_skills or '[]')
        except Exception:
            return []

    @required_skills.setter
    def required_skills(self, val):
        self._required_skills = json.dumps(val if isinstance(val, list) else [])

    @property
    def required_skill_levels(self):
        try:
            return json.loads(self._required_skill_levels or '[]')
        except Exception:
            return []

    @required_skill_levels.setter
    def required_skill_levels(self, val):
        self._required_skill_levels = json.dumps(val if isinstance(val, list) else [])

    @property
    def application_questions(self):
        try:
            return json.loads(self._application_questions or '[]')
        except Exception:
            return []

    @application_questions.setter
    def application_questions(self, val):
        self._application_questions = json.dumps(val if isinstance(val, list) else [])


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('industry_profiles.id', ondelete='SET NULL'), nullable=True)
    resume_file_path = db.Column(db.String(255), nullable=False)
    _answers_to_questions = db.Column('answers_to_questions', db.Text, default='[]')
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Applied")  # Applied, Under Review, Shortlisted, Interview, Selected, Rejected
    status_updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    skill_match_score = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint('student_id', 'opportunity_id', name='uq_student_opportunity_app'),)

    @property
    def answers_to_questions(self):
        try:
            return json.loads(self._answers_to_questions or '[]')
        except Exception:
            return []

    @answers_to_questions.setter
    def answers_to_questions(self, val):
        self._answers_to_questions = json.dumps(val if isinstance(val, list) else [])


class LearningResource(db.Model):
    __tablename__ = 'learning_resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    difficulty = db.Column(db.String(50), default="Beginner")  # Beginner, Intermediate, Advanced
    external_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_free = db.Column(db.Boolean, default=True)
    resource_type = db.Column(db.String(50), default="Course")  # Video, Course, Documentation, Practice
    duration = db.Column(db.String(50), default="4-6 hours")
    why_recommended = db.Column(db.String(255), default="High-priority verified skill recommendation")
    is_verified_resource = db.Column(db.Boolean, default=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


class Collaboration(db.Model):
    __tablename__ = 'collaborations'
    id = db.Column(db.Integer, primary_key=True)
    academician_id = db.Column(db.Integer, db.ForeignKey('academician_profiles.id', ondelete='CASCADE'), nullable=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industry_profiles.id', ondelete='CASCADE'), nullable=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution_profiles.id', ondelete='CASCADE'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    collaboration_type = db.Column(db.String(100), nullable=False)  # Guest Lecture, Workshop, Research, Live Project, etc.
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), default="1 Semester")
    commitment = db.Column(db.String(100), default="4 hours / week")
    skills_needed = db.Column(db.String(255), default="GenAI, Full Stack Systems")
    deliverables = db.Column(db.Text, default="Joint curriculum development and student mentorship")
    status = db.Column(db.String(50), default="Proposed")  # Proposed, Accepted, Active, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    related_id = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'related_id': self.related_id,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }
