from datetime import datetime, timedelta
from models import (
    db, Skill, StudentSkill, CareerRequirement,
    LearningResource, Notification, IndustryProfile
)

def calculate_skill_match(student, opportunity):
    """
    Calculate Skill Match percentage between a student's verified skills
    and an opportunity's required skills.
    
    Formula:
    For each required skill:
      If student has verified score:
        contribution = min(1.0, verified_score / required_level_score)
      Else:
        contribution = 0 (unassessed = 0)
    Final Match = (sum(contributions) / count(required_skills)) * 100
    """
    required_skills = opportunity.required_skills
    required_levels = opportunity.required_skill_levels
    
    if not required_skills:
        return {
            'match_percentage': 100,
            'matching_skills': [],
            'gap_skills': [],
            'why_match': ["No specific skills required"]
        }

    # Map level string to target benchmark score
    level_targets = {
        'beginner': 50,
        'intermediate': 70,
        'advanced': 85
    }

    # Fetch student's verified skills
    student_skills_map = {}
    for ss in student.skills:
        if ss.is_verified and ss.verified_score is not None:
            skill_name = ss.skill_ref.name if ss.skill_ref else ""
            student_skills_map[skill_name.lower()] = ss.verified_score

    contributions = []
    matching_skills = []
    gap_skills = []
    why_match = []

    for i, req_skill in enumerate(required_skills):
        level_str = required_levels[i].lower() if i < len(required_levels) else 'intermediate'
        target_score = level_targets.get(level_str, 70)
        
        # Match case-insensitively
        score = student_skills_map.get(req_skill.lower())

        if score is not None:
            contribution = min(1.0, score / target_score)
            contributions.append(contribution)
            if score >= target_score * 0.8:
                matching_skills.append({
                    'skill': req_skill,
                    'score': score,
                    'target': target_score,
                    'level': level_str.capitalize()
                })
                why_match.append(f"✓ {req_skill} verified at {score}/100")
            else:
                gap_skills.append({
                    'skill': req_skill,
                    'score': score,
                    'target': target_score,
                    'gap': target_score - score,
                    'level': level_str.capitalize()
                })
        else:
            contributions.append(0.0)
            gap_skills.append({
                'skill': req_skill,
                'score': None,
                'target': target_score,
                'gap': target_score,
                'level': level_str.capitalize()
            })

    match_percentage = int(round((sum(contributions) / len(required_skills)) * 100))

    # Add career goal alignment note
    if student.career_goal and student.career_goal.lower() in opportunity.title.lower():
        why_match.append(f"Aligms directly with your '{student.career_goal}' career goal")

    return {
        'match_percentage': match_percentage,
        'matching_skills': matching_skills,
        'gap_skills': gap_skills,
        'why_match': why_match
    }


def calculate_skill_gaps(student):
    """
    Compute required skills, current scores, and gaps for the student's career goal.
    Priority thresholds:
      Gap >= 35: HIGH PRIORITY (red)
      Gap 15-34: MEDIUM PRIORITY (orange)
      Gap < 15: LOW PRIORITY (green)
      Unassessed: UNASSESSED (gray)
    """
    career_req = CareerRequirement.query.filter_by(career_goal=student.career_goal).first()
    if not career_req:
        career_req = CareerRequirement.query.filter_by(career_goal="Software Developer").first()

    required_skills = career_req.required_skills if career_req else ["C Programming", "Data Structures", "Problem Solving", "Communication", "Algorithms"]
    minimum_scores = career_req.minimum_scores if career_req else [70, 75, 70, 60, 70]

    # Map verified skills
    verified_map = {}
    for ss in student.skills:
        if ss.is_verified and ss.verified_score is not None:
            name = ss.skill_ref.name if ss.skill_ref else ""
            verified_map[name.lower()] = {
                'score': ss.verified_score,
                'verified_date': ss.verified_date,
                'skill_id': ss.skill_id
            }

    skills_data = []
    strong_skills = []
    skills_to_improve = []
    assessed_count = 0

    for i, skill_name in enumerate(required_skills):
        min_score = minimum_scores[i] if i < len(minimum_scores) else 70
        verified_info = verified_map.get(skill_name.lower())

        # Find corresponding skill in DB for ID
        skill_obj = Skill.query.filter_by(name=skill_name).first()
        skill_id = skill_obj.id if skill_obj else None

        if verified_info:
            current_score = verified_info['score']
            gap = max(0, min_score - current_score)
            is_assessed = True
            assessed_count += 1
            
            if gap >= 35:
                priority = 'HIGH PRIORITY'
                priority_class = 'danger'
            elif gap >= 15:
                priority = 'MEDIUM PRIORITY'
                priority_class = 'warning'
            else:
                priority = 'LOW PRIORITY'
                priority_class = 'success'
        else:
            current_score = None
            gap = min_score
            is_assessed = False
            priority = 'UNASSESSED'
            priority_class = 'secondary'

        item = {
            'skill_id': skill_id,
            'name': skill_name,
            'current_score': current_score,
            'required_score': min_score,
            'gap': gap,
            'is_assessed': is_assessed,
            'priority': priority,
            'priority_class': priority_class
        }
        skills_data.append(item)

        if is_assessed and current_score >= min_score:
            strong_skills.append(item)
        else:
            skills_to_improve.append(item)

    # Sort priorities: unassessed and high gaps first
    top_priorities = sorted(skills_to_improve, key=lambda x: (x['is_assessed'], -x['gap']))[:3]

    return {
        'career_goal': student.career_goal,
        'total_required': len(required_skills),
        'assessed_count': assessed_count,
        'all_skills': skills_data,
        'strong_skills': strong_skills,
        'skills_to_improve': skills_to_improve,
        'top_priorities': top_priorities
    }


def calculate_career_readiness(student):
    """
    Transparent, component-based Career Readiness score.
    Formula:
      readiness = (technical_coverage * 0.35)
                + (skill_quality * 0.30)
                + (soft_skills_avg * 0.20)
                + (learning_progress * 0.15)
    """
    gaps_info = calculate_skill_gaps(student)
    total_required = gaps_info['total_required']
    assessed_count = gaps_info['assessed_count']
    
    # 1. Technical coverage: fraction of required skills assessed
    coverage_ratio = (assessed_count / total_required) if total_required > 0 else 0.5
    
    # 2. Skill quality: avg score of assessed skills vs requirements
    quality_scores = []
    for s in gaps_info['all_skills']:
        if s['is_assessed']:
            ratio = min(1.0, s['current_score'] / s['required_score'])
            quality_scores.append(ratio)
    avg_quality = (sum(quality_scores) / len(quality_scores)) if quality_scores else 0.4

    # 3. Soft skills average
    soft_skills = []
    for ss in student.skills:
        if ss.is_verified and ss.skill_ref and ss.skill_ref.category == 'soft':
            soft_skills.append(ss.verified_score / 100.0)
    avg_soft = (sum(soft_skills) / len(soft_skills)) if soft_skills else 0.70

    # 4. Learning progress: based on assessment attempts completed
    attempts_count = student.attempts.count()
    learning_progress = min(1.0, max(0.4, attempts_count / 3.0))

    readiness = (coverage_ratio * 0.35) + (avg_quality * 0.30) + (avg_soft * 0.20) + (learning_progress * 0.15)
    readiness_percentage = int(round(readiness * 100))

    return {
        'overall': min(100, max(15, readiness_percentage)),
        'components': {
            'technical_coverage': int(round(coverage_ratio * 100)),
            'skill_quality': int(round(avg_quality * 100)),
            'soft_skills': int(round(avg_soft * 100)),
            'learning_progress': int(round(learning_progress * 100))
        },
        'assessed_count': assessed_count,
        'total_required': total_required
    }


def get_personalized_learning(student):
    """
    Returns ranked and categorized learning resources based on:
    1. Highest skill gaps
    2. Career goal required skills
    3. Interested domains
    """
    gaps_info = calculate_skill_gaps(student)
    top_gap_names = [s['name'].lower() for s in gaps_info['skills_to_improve']]
    interested_domains = [d.lower() for d in student.interested_domains]

    all_resources = LearningResource.query.all()
    recommended = []

    for res in all_resources:
        skill_name = res.skill.name.lower() if res.skill else ""
        category_lower = res.category.lower()
        score = 0
        reasons = []

        if skill_name in top_gap_names:
            score += 50
            reasons.append(f"High-priority skill gap in '{res.skill.name}' for your goal")

        if any(d in category_lower or d in res.title.lower() for d in interested_domains):
            score += 30
            reasons.append(f"Matches your interested domain: {res.category}")

        if student.career_goal.lower() in res.description.lower() or student.career_goal.lower() in res.title.lower():
            score += 20
            reasons.append(f"Key resource for {student.career_goal}")

        res.match_score = score
        res.custom_reason = " • ".join(reasons) if reasons else res.why_recommended
        recommended.append(res)

    recommended.sort(key=lambda r: r.match_score, reverse=True)
    return recommended


def create_notification(user_id, event_type, message, related_id=None):
    """Safely create a database notification."""
    notif = Notification(
        user_id=user_id,
        event_type=event_type,
        message=message,
        related_id=related_id,
        read=False
    )
    db.session.add(notif)
    db.session.commit()
    return notif


def record_profile_view(viewer_user_id, student_profile):
    """
    Deduplicate profile view notification:
    Maximum 1 notification per company per 24 hours.
    """
    company_profile = IndustryProfile.query.filter_by(user_id=viewer_user_id).first()
    company_name = company_profile.company_name if company_profile else "An industry partner"

    # Check for notification in past 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    existing = Notification.query.filter(
        Notification.user_id == student_profile.user_id,
        Notification.event_type == 'profile_viewed',
        Notification.message.like(f"%{company_name}%"),
        Notification.created_at >= cutoff
    ).first()

    if not existing:
        create_notification(
            user_id=student_profile.user_id,
            event_type='profile_viewed',
            message=f"{company_name} viewed your candidate profile."
        )
