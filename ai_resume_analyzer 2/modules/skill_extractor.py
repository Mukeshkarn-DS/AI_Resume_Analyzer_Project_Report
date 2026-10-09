"""
Skill Extractor Module
Extracts skills and contact information from resume text.
"""

import re
import json
import os

# Load skills database
SKILLS_DB_PATH = os.path.join("data", "skills_db.json")

with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
    SKILLS_DB = json.load(f)


def extract_contact_info(text):
    """Extract contact information from resume text."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)

    phone_pattern = r"(\+?\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}"
    phone_match = re.search(phone_pattern, text)
    phone_str = phone_match.group(0).strip() if phone_match else ""

    linkedin_pattern = r"(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9\-_]+)"
    linkedins = re.findall(linkedin_pattern, text, re.IGNORECASE)

    github_pattern = r"(?:github\.com/)([A-Za-z0-9\-_]+)"
    githubs = re.findall(github_pattern, text, re.IGNORECASE)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    name = lines[0][:60] if lines else "Not found"
    if "@" in name or any(c.isdigit() for c in name):
        name = lines[1][:60] if len(lines) > 1 else "Not found"

    return {
        "name": name,
        "email": emails[0] if emails else "Not found",
        "phone": phone_str if phone_str else "Not found",
        "linkedin": f"linkedin.com/in/{linkedins[0]}" if linkedins else "Not found",
        "github": f"github.com/{githubs[0]}" if githubs else "Not found",
    }


def extract_skills(text):
    """Extract skills from resume text by matching against skills database."""
    text_lower = text.lower()
    found_skills = set()

    for skill in SKILLS_DB:
        pattern = r"(?<![a-zA-Z])" + re.escape(skill.lower()) + r"(?![a-zA-Z])"
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    return sorted(found_skills, key=str.lower)


def extract_education(text):
    """Extract education qualifications."""
    edu_keywords = {
        "b.tech": "B.Tech", "btech": "B.Tech", "b.e": "B.E",
        "b.sc": "B.Sc", "bsc": "B.Sc", "bca": "BCA",
        "mca": "MCA", "m.tech": "M.Tech", "mtech": "M.Tech",
        "m.sc": "M.Sc", "msc": "M.Sc", "mba": "MBA",
        "bachelor": "Bachelor's", "master": "Master's",
        "phd": "PhD", "diploma": "Diploma",
    }

    text_lower = text.lower()
    found = []
    for key, value in edu_keywords.items():
        if key in text_lower and value not in found:
            found.append(value)

    return found