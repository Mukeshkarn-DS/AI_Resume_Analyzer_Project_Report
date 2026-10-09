"""
Offline training script. Run once before deploying ML features.

Usage:
    python -m ml_pipeline.train_pipeline
"""
import os
import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .feature_engineering import (
    extract_advanced_features,
    features_to_vector,
    FEATURE_ORDER,
)
from .evaluation import (
    evaluate_resume_scorer,
    evaluate_skill_extraction,
)


def train_resume_scorer():
    """
    Train ML scorer from labeled_resumes.csv.
    Expected columns: text, score (0-100)
    """
    path = "data/labeled_resumes.csv"
    if not os.path.exists(path):
        print("[SKIP] No labeled_resumes.csv. Create it with columns: text,score")
        return

    df = pd.read_csv(path)
    X, y = [], []
    for _, row in df.iterrows():
        feats = extract_advanced_features(row["text"], [], {})
        X.append(features_to_vector(feats, FEATURE_ORDER))
        y.append(float(row["score"]))
    X, y = np.array(X), np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("Resume Scorer Metrics:", evaluate_resume_scorer(y_test, preds))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/resume_scorer.pkl")
    print("Saved models/resume_scorer.pkl")


def train_job_classifier():
    """
    Train a job-role classifier from jobs_dataset.csv (augmented).
    """
    path = "data/jobs_dataset.csv"
    if not os.path.exists(path):
        print("[SKIP] jobs_dataset.csv missing.")
        return

    df = pd.read_csv(path)
    X = df["job_description"].fillna("") + " " + df["required_skills"].fillna("")
    y = df["job_role"]

    if y.nunique() < 2 or len(df) < 20:
        print("[WARN] Too few samples to train meaningful classifier.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipe.fit(X_train, y_train)

    from sklearn.metrics import accuracy_score, classification_report
    preds = pipe.predict(X_test)
    print("Job Classifier Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    os.makedirs("models", exist_ok=True)
    joblib.dump(pipe, "models/job_classifier.pkl")
    print("Saved models/job_classifier.pkl")


def train_xgb_ranker():
    """
    Train XGBoost Learning-to-Rank.
    Requires data/ltr_training.csv with columns:
      query_id, resume_text, job_role, required_skills, job_description, relevance
    """
    path = "data/ltr_training.csv"
    if not os.path.exists(path):
        print("[SKIP] ltr_training.csv missing.")
        return

    try:
        import xgboost as xgb
    except ImportError:
        print("[SKIP] xgboost not installed.")
        return

    df = pd.read_csv(path)

    # Build features per (query, doc)
    from sklearn.metrics.pairwise import cosine_similarity
    from sentence_transformers import SentenceTransformer

    sbert = SentenceTransformer("all-MiniLM-L6-v2")

    features, labels, groups = [], [], []
    for qid, group in df.groupby("query_id"):
        q_emb = sbert.encode([group.iloc[0]["resume_text"]], normalize_embeddings=True)
        d_embs = sbert.encode(
            (group["job_description"] + " " + group["required_skills"]).tolist(),
            normalize_embeddings=True,
        )
        sims = cosine_similarity(q_emb, d_embs).flatten()
        for sim, (_, row) in zip(sims, group.iterrows()):
            features.append([sim, row.get("skill_overlap", 0), row.get("exp_match", 0)])
            labels.append(row["relevance"])
        groups.append(len(group))

    features = np.array(features)
    labels = np.array(labels)

    ranker = xgb.XGBRanker(
        objective="rank:pairwise",
        learning_rate=0.1,
        n_estimators=100,
        max_depth=6,
    )
    ranker.fit(features, labels, group=groups)

    os.makedirs("models", exist_ok=True)
    ranker.save_model("models/xgb_ranker.json")
    print("Saved models/xgb_ranker.json")


if __name__ == "__main__":
    print("=== Training Resume Scorer ===")
    train_resume_scorer()
    print("\n=== Training Job Classifier ===")
    train_job_classifier()
    print("\n=== Training XGBoost Ranker ===")
    train_xgb_ranker()
    print("\nDone.")