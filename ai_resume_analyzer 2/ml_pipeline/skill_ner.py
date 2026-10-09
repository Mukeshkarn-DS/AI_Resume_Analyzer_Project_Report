"""
Skill NER Module
Extracts skills using spaCy PhraseMatcher against a skills database.
"""

import os
import json
import spacy
from spacy.matcher import PhraseMatcher

SKILLS_DB_PATH = os.path.join("data", "skills_db.json")

_nlp = None
_matcher = None


def _init():
    """Initialize spaCy model and PhraseMatcher (once)."""
    global _nlp, _matcher
    if _matcher is not None:
        return

    _nlp = spacy.load("en_core_web_sm")
    _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")

    # Load skills database
    if not os.path.exists(SKILLS_DB_PATH):
        raise FileNotFoundError(f"Skills DB not found: {SKILLS_DB_PATH}")

    with open(SKILLS_DB_PATH, "r") as f:
        data = json.load(f)

    # Support both list and dict formats
    skills = []
    if isinstance(data, dict):
        for cat, items in data.items():
            for item in items:
                if isinstance(item, dict):
                    skills.append(item.get("name", ""))
                else:
                    skills.append(item)
    else:
        skills = data

    skills = [s for s in skills if s and isinstance(s, str)]

    if skills:
        patterns = [_nlp.make_doc(s) for s in skills]
        _matcher.add("SKILLS", patterns)


def extract_skills_ner(text):
    """
    Extract skills from resume text.

    Args:
        text (str): Raw resume text.

    Returns:
        list: Sorted list of unique skill names (lowercase).
    """
    _init()
    doc = _nlp(text)
    matches = _matcher(doc)

    found = set()
    for _, start, end in matches:
        found.add(doc[start:end].text.lower())

    return sorted(found)


# Fallback alias in case other modules import extract_skills
extract_skills = extract_skills_ner