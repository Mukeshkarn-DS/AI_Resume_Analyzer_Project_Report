"""
Evaluation Metrics Module
"""

import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    ndcg_score, mean_absolute_error, mean_squared_error,
)


def evaluate_skill_extraction(y_true, y_pred):
    return {
        "precision_micro": precision_score(y_true, y_pred, average="micro", zero_division=0),
        "recall_micro": recall_score(y_true, y_pred, average="micro", zero_division=0),
        "f1_micro": f1_score(y_true, y_pred, average="micro", zero_division=0),
    }


def evaluate_recommendation(y_true_relevance, y_scores, k=5):
    try:
        return {f"ndcg@{k}": float(ndcg_score(y_true_relevance, y_scores, k=k))}
    except Exception:
        return {f"ndcg@{k}": 0.0}


def evaluate_resume_scorer(y_true, y_pred):
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "pearson_r": float(np.corrcoef(y_true, y_pred)[0, 1]),
    }