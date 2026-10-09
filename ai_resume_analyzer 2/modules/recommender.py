"""
Job Recommender Module
Uses TF-IDF and Cosine Similarity to recommend job roles.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Load jobs dataset
JOBS_PATH = os.path.join("data", "jobs_dataset.csv")
JOBS_DF = pd.read_csv(JOBS_PATH)

# Global variables for optimization
_vectorizer = None
_job_vectors = None


def _initialize_vectorizer():
    """Initialize and fit the TF-IDF vectorizer on job descriptions."""
    global _vectorizer, _job_vectors

    if _vectorizer is None:
        _vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            lowercase=True,
        )
        job_texts = JOBS_DF["job_description"].fillna("").tolist()
        _job_vectors = _vectorizer.fit_transform(job_texts)

    return _vectorizer, _job_vectors


def recommend_jobs(resume_text, skills, top_n=5):
    """Recommend top-N job roles based on resume text and skills."""
    vectorizer, job_vectors = _initialize_vectorizer()

    skills_text = " ".join(skills) * 2
    resume_combined = resume_text + " " + skills_text

    resume_vector = vectorizer.transform([resume_combined])
    similarities = cosine_similarity(resume_vector, job_vectors).flatten()

    top_indices = similarities.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        row = JOBS_DF.iloc[idx]
        match_pct = round(float(similarities[idx]) * 100, 2)

        if match_pct < 5:
            continue

        results.append({
            "job_role": row["job_role"],
            "match_percent": match_pct,
            "required_skills": row["required_skills"],
            "education": row.get("education", "N/A"),
            "experience": row.get("experience", "N/A"),
        })

    return results