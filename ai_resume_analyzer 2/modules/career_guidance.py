"""
Career Guidance Module
Identifies skill gaps and recommends courses.
Also provides overall advice based on resume score.
"""

import json
import os

# Load course mapping
COURSES_PATH = os.path.join("data", "courses.json")

try:
    with open(COURSES_PATH, "r") as f:
        COURSE_MAP = json.load(f)
except FileNotFoundError:
    print(f"[WARN] {COURSES_PATH} not found. Course recommendations disabled.")
    COURSE_MAP = {}
except json.JSONDecodeError as e:
    print(f"[WARN] Invalid JSON in {COURSES_PATH}: {e}")
    COURSE_MAP = {}


def get_career_guidance(user_skills, recommendations):
    """
    Generate personalized career guidance.

    Args:
        user_skills (list): Skills extracted from resume.
        recommendations (list): Job recommendations.

    Returns:
        list: Guidance per job role with missing skills and courses.
    """
    user_skills_set = {s.lower().strip() for s in user_skills}
    guidance_list = []

    for rec in recommendations[:3]:  # Top 3 roles only
        job_role = rec.get("job_role", "")
        required_raw = rec.get("required_skills", "")

        required = [
            s.strip().lower()
            for s in str(required_raw).split(",")
            if s.strip()
        ]

        # Identify missing skills
        missing = [s for s in required if s not in user_skills_set]

        # Get courses for missing skills
        courses = []
        for skill in missing:
            if skill in COURSE_MAP:
                for course in COURSE_MAP[skill]:
                    courses.append({
                        "skill": skill,
                        "course_name": course.get("name", "Unknown"),
                        "platform": course.get("platform", "N/A"),
                        "url": course.get("url", "#"),
                        "duration": course.get("duration", "N/A"),
                    })

        # Calculate readiness
        if required:
            readiness = round(
                (len(required) - len(missing)) / len(required) * 100, 2
            )
        else:
            readiness = 0

        guidance_list.append({
            "job_role": job_role,
            "match_percent": rec.get("match_percent", 0),
            "readiness": readiness,
            "missing_skills": missing,
            "courses": courses,
            "total_required": len(required),
            "total_matched": len(required) - len(missing),
        })

    return guidance_list


def get_overall_guidance(skills, score_data):
    """
    Generate overall career advice based on resume score.

    Args:
        skills (list): Extracted skills.
        score_data (dict): Dict with 'total' key (score).

    Returns:
        list: List of advice dicts with 'type' and 'message'.
    """
    advice = []

    total_score = score_data.get("total", 0)

    if total_score >= 85:
        advice.append({
            "type": "success",
            "message": "Excellent resume! Start applying to top companies."
        })
    elif total_score >= 70:
        advice.append({
            "type": "info",
            "message": "Good resume! Minor improvements can make it stand out."
        })
    elif total_score >= 50:
        advice.append({
            "type": "warning",
            "message": "Average resume. Focus on adding projects and skills."
        })
    else:
        advice.append({
            "type": "danger",
            "message": "Resume needs significant improvement. Follow recommendations below."
        })

    # Skill count advice
    if len(skills) < 8:
        advice.append({
            "type": "info",
            "message": f"You have {len(skills)} skills. Aim for 12-15 relevant skills."
        })
    elif len(skills) >= 15:
        advice.append({
            "type": "success",
            "message": f"Great! You have {len(skills)} skills listed."
        })

    return advice