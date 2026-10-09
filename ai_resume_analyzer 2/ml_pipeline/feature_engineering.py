"""
Feature Engineering Module
Extracts 20 advanced features from resume text for ML scoring.
"""

import re
import spacy
import numpy as np

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

nlp = spacy.load("en_core_web_sm")

ACTION_VERBS = {
    "developed", "led", "managed", "created", "built", "optimized",
    "designed", "implemented", "improved", "launched", "delivered",
    "architected", "automated", "reduced", "increased", "achieved"
}

SECTION_KEYWORDS = {
    "education": ["education", "academic", "qualification"],
    "experience": ["experience", "employment", "work history", "internship"],
    "projects": ["project", "projects", "portfolio"],
    "skills": ["skills", "technical skills", "competencies"],
    "certifications": ["certification", "certificate", "license"],
    "awards": ["award", "achievement", "honor"],
}


def extract_advanced_features(text, skills, contact):
    """Extract 20 advanced features from resume."""
    doc = nlp(text)
    text_lower = text.lower()
    features = {}

    verbs = [t.lemma_.lower() for t in doc if t.pos_ == "VERB"]
    features["action_verb_count"] = sum(1 for v in verbs if v in ACTION_VERBS)
    features["verb_density"] = len(verbs) / max(len(text.split()), 1)

    numbers = re.findall(r"\b\d+(?:\.\d+)?%?\b", text)
    features["quantified_count"] = len(numbers)
    features["quantified_density"] = len(numbers) / max(len(text.split()), 1)

    if HAS_TEXTSTAT:
        try:
            features["flesch_reading_ease"] = textstat.flesch_reading_ease(text)
            features["flesch_kincaid_grade"] = textstat.flesch_kincaid_grade(text)
        except Exception:
            features["flesch_reading_ease"] = 0.0
            features["flesch_kincaid_grade"] = 0.0
    else:
        features["flesch_reading_ease"] = 0.0
        features["flesch_kincaid_grade"] = 0.0

    for sec, kws in SECTION_KEYWORDS.items():
        features[f"has_{sec}"] = int(any(kw in text_lower for kw in kws))

    features["skill_count"] = len(skills)
    features["skill_density"] = len(skills) / max(len(text.split()) / 100, 1)

    features["has_email"] = int(contact.get("email") not in (None, "Not found"))
    features["has_phone"] = int(contact.get("phone") not in (None, "Not found"))
    features["has_linkedin"] = int(contact.get("linkedin") not in (None, "Not found"))
    features["has_github"] = int(contact.get("github") not in (None, "Not found"))

    words = text.split()
    features["word_count"] = len(words)
    features["avg_word_length"] = (
        float(np.mean([len(w) for w in words])) if words else 0.0
    )

    return features


FEATURE_ORDER = [
    "action_verb_count", "verb_density",
    "quantified_count", "quantified_density",
    "flesch_reading_ease", "flesch_kincaid_grade",
    "has_education", "has_experience", "has_projects",
    "has_skills", "has_certifications", "has_awards",
    "skill_count", "skill_density",
    "has_email", "has_phone", "has_linkedin", "has_github",
    "word_count", "avg_word_length",
]


def features_to_vector(features, feature_order=None):
    if feature_order is None:
        feature_order = FEATURE_ORDER
    return np.array([features.get(k, 0.0) for k in feature_order], dtype=float)