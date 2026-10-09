"""
Hybrid Job Recommender using SBERT + TF-IDF fallback.
"""

import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SBERT_MODEL_NAME = "all-MiniLM-L6-v2"
JOBS_PATH = os.path.join("data", "jobs_dataset.csv")

_jobs_df = None
_sbert = None
_job_embeddings = None
_tfidf_vectorizer = None
_tfidf_matrix = None


def _load_jobs():
    global _jobs_df
    if _jobs_df is None:
        _jobs_df = pd.read_csv(JOBS_PATH)
        _jobs_df["job_description"] = _jobs_df["job_description"].fillna("")
        _jobs_df["required_skills"] = _jobs_df["required_skills"].fillna("")
    return _jobs_df


def _init_sbert():
    global _sbert, _job_embeddings
    if _sbert is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _sbert = SentenceTransformer(SBERT_MODEL_NAME)
        jobs = _load_jobs()
        texts = (
            jobs["job_role"] + " "
            + jobs["job_description"] + " "
            + jobs["required_skills"]
        ).tolist()
        _job_embeddings = _sbert.encode(texts, normalize_embeddings=True)
    except Exception as e:
        print(f"[WARN] SBERT failed: {e}")
        _sbert = None


def _init_tfidf():
    global _tfidf_vectorizer, _tfidf_matrix
    if _tfidf_vectorizer is not None:
        return
    jobs = _load_jobs()
    _tfidf_vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
    )
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(
        jobs["job_description"].tolist()
    )


def recommend_jobs_ltr(resume_text, skills, top_n=5):
    """Recommend top N jobs using SBERT or TF-IDF fallback."""
    jobs = _load_jobs()
    _init_sbert()
    _init_tfidf()

    query = resume_text + " " + (" ".join(skills) * 2)

    if _sbert is not None:
        q_emb = _sbert.encode([query], normalize_embeddings=True)
        sims = cosine_similarity(q_emb, _job_embeddings).flatten()
    else:
        query_vec = _tfidf_vectorizer.transform([query])
        sims = cosine_similarity(query_vec, _tfidf_matrix).flatten()

    top_indices = np.argsort(sims)[::-1][:top_n]
    results = []
    for idx in top_indices:
        row = jobs.iloc[idx]
        match_pct = round(float(sims[idx]) * 100, 2)
        if match_pct < 5:
            continue
        results.append({
            "job_role": row["job_role"],
            "match_percent": match_pct,
            "required_skills": row["required_skills"],
            "education": row.get("education", "N/A"),
            "experience": row.get("experience", "N/A"),
            "explanation": f"Semantic match based on {len(skills)} skills.",
        })
    return results