"""
Resume Scorer Module
Calculates comprehensive resume score based on 6 criteria.
"""


def calculate_resume_score(text, skills, contact):
    """Calculate resume score out of 100."""
    score = 0
    breakdown = {}
    recommendations = []
    text_lower = text.lower()

    # 1. Contact Info (10 points)
    contact_score = 0
    if contact.get("email") and contact["email"] != "Not found":
        contact_score += 4
    else:
        recommendations.append("Add your email address")

    if contact.get("phone") and contact["phone"] != "Not found":
        contact_score += 3
    else:
        recommendations.append("Add your phone number")

    if contact.get("linkedin") and contact["linkedin"] != "Not found":
        contact_score += 3
    else:
        recommendations.append("Add your LinkedIn profile URL")

    breakdown["Contact Info"] = contact_score
    score += contact_score

    # 2. Skills (30 points)
    skill_count = len(skills)
    skill_score = min(skill_count, 15) * 2
    breakdown["Skills"] = skill_score
    score += skill_score

    if skill_count < 10:
        recommendations.append(
            f"Add more relevant technical skills (found {skill_count}, aim for 10-15)"
        )

    # 3. Education (15 points)
    edu_keywords = [
        "b.tech", "btech", "b.e", "b.sc", "bsc", "bca",
        "mca", "m.tech", "mtech", "m.sc", "msc",
        "bachelor", "master", "phd", "diploma"
    ]
    edu_found = any(kw in text_lower for kw in edu_keywords)
    edu_score = 15 if edu_found else 5
    breakdown["Education"] = edu_score
    score += edu_score

    if not edu_found:
        recommendations.append("Add your educational qualifications")

    # 4. Experience (20 points)
    exp_keywords = [
        "experience", "internship", "worked", "company",
        "organization", "employment", "years of experience"
    ]
    exp_found = any(kw in text_lower for kw in exp_keywords)
    exp_score = 20 if exp_found else 5
    breakdown["Experience"] = exp_score
    score += exp_score

    if not exp_found:
        recommendations.append("Add work experience or internships")

    # 5. Projects (15 points)
    proj_keywords = ["project", "projects", "developed", "built", "created"]
    proj_found = any(kw in text_lower for kw in proj_keywords)
    proj_score = 15 if proj_found else 3
    breakdown["Projects"] = proj_score
    score += proj_score

    if not proj_found:
        recommendations.append("Add a Projects section with 2-3 projects")

    # 6. Formatting (10 points)
    word_count = len(text.split())
    if 200 <= word_count <= 1000:
        fmt_score = 10
    elif 100 <= word_count < 200 or 1000 < word_count <= 1500:
        fmt_score = 7
    else:
        fmt_score = 4

    breakdown["Formatting"] = fmt_score
    score += fmt_score

    if word_count < 200:
        recommendations.append("Resume is too short. Add more details.")
    elif word_count > 1000:
        recommendations.append("Resume is too long. Keep it concise (1-2 pages).")

    # Final score
    total_score = min(score, 100)

    if total_score >= 85:
        grade, grade_color = "Excellent", "green"
    elif total_score >= 70:
        grade, grade_color = "Good", "blue"
    elif total_score >= 50:
        grade, grade_color = "Average", "orange"
    else:
        grade, grade_color = "Needs Improvement", "red"

    return {
        "total": total_score,
        "breakdown": breakdown,
        "grade": grade,
        "grade_color": grade_color,
        "recommendations": recommendations,
        "word_count": word_count,
    }