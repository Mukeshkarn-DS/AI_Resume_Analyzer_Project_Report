"""
Bias and Fairness Metrics
"""

try:
    from fairlearn.metrics import (
        demographic_parity_difference,
        equalized_odds_difference,
        MetricFrame,
    )
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    HAS_FAIRLEARN = True
except ImportError:
    HAS_FAIRLEARN = False


def compute_fairness_metrics(y_true, y_pred, sensitive_features):
    if not HAS_FAIRLEARN:
        return {"error": "fairlearn not installed"}

    metrics = {
        "accuracy": accuracy_score,
        "precision": lambda yt, yp: precision_score(yt, yp, zero_division=0),
        "recall": lambda yt, yp: recall_score(yt, yp, zero_division=0),
    }
    try:
        mf = MetricFrame(
            metrics=metrics,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_features,
        )
        return {
            "by_group": mf.by_group.to_dict(),
            "difference": mf.difference().to_dict(),
            "demographic_parity_diff": float(
                demographic_parity_difference(
                    y_true, y_pred, sensitive_features=sensitive_features
                )
            ),
            "equalized_odds_diff": float(
                equalized_odds_difference(
                    y_true, y_pred, sensitive_features=sensitive_features
                )
            ),
        }
    except Exception as e:
        return {"error": str(e)}