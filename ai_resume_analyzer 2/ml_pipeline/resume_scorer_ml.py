"""
ML Resume Scorer Module
Uses a trained Random Forest regressor or falls back to heuristic.
"""

import os
import joblib
import numpy as np

from .feature_engineering import (
    extract_advanced_features,
    features_to_vector,
    FEATURE_ORDER,
)

MODEL_PATH = os.path.join("models", "resume_scorer.pkl")
_model = None


def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception:
            _model = None
    return _model


def predict_resume_score(text, skills, contact):
    """Predict resume score using ML model or heuristic fallback."""
    features = extract_advanced_features(text, skills, contact)
    X = features_to_vector(features, FEATURE_ORDER).reshape(1, -1)

    model = _load_model()
    if model is not None:
        try:
            score = float(np.clip(model.predict(X)[0], 0, 100))
            return {
                "score": round(score, 2),
                "features": features,
                "source": "ml",
            }
        except Exception:
            pass

    # Heuristic fallback
    score = (
        features["action_verb_count"] * 2
        + features["quantified_count"] * 3
        + features["skill_count"] * 2
        + features["has_education"] * 10
        + features["has_experience"] * 15
        + features["has_projects"] * 10
        + features["has_email"] * 4
        + features["has_phone"] * 3
        + features["has_linkedin"] * 3
    )
    score = float(np.clip(score, 0, 100))

    return {
        "score": round(score, 2),
        "features": features,
        "source": "heuristic",
    }