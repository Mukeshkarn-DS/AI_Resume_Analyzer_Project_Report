"""
Explainability utilities: SHAP for tabular ranker, LIME for text classifier.
"""
import numpy as np


def explain_recommendation(model, features, feature_names):
    """
    SHAP explanation for a tabular model (e.g., XGBoost ranker).
    Returns dict: feature -> shap value.
    """
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        return {
            name: float(val)
            for name, val in zip(feature_names, np.array(shap_values).flatten())
        }
    except Exception as e:
        return {"error": str(e)}


def explain_text_prediction(model_predict_proba, text, class_names, num_features=10):
    """
    LIME explanation for text models.
    """
    try:
        from lime.lime_text import LimeTextExplainer
        explainer = LimeTextExplainer(class_names=class_names)
        exp = explainer.explain_instance(
            text, model_predict_proba, num_features=num_features
        )
        return exp.as_list()
    except Exception as e:
        return [("error", str(e))]