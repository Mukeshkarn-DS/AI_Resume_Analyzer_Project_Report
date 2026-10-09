"""
Main ML pipeline. One-stop shop for the Flask app.
"""
from .skill_ner import extract_skills_ner
from .feature_engineering import extract_advanced_features
from .resume_scorer_ml import predict_resume_score
from .job_recommender_ltr import recommend_jobs_ltr
from .explainability import explain_recommendation


class MLPipeline:
    def __init__(self, use_ml_scorer=True, use_ltr=True):
        self.use_ml_scorer = use_ml_scorer
        self.use_ltr = use_ltr

    def run(self, resume_text: str, contact: dict) -> dict:
        """
        Full pipeline: skills -> score -> jobs -> explanation.
        """
        # 1. Skills
        skills = extract_skills_ner(resume_text)

        # 2. Score
        if self.use_ml_scorer:
            score_result = predict_resume_score(resume_text, skills, contact)
        else:
            from modules.scorer import calculate_resume_score
            legacy = calculate_resume_score(resume_text, skills, contact)
            score_result = {
                "score": legacy["total"],
                "features": {},
                "source": "heuristic",
            }

        # 3. Job recommendation
        if self.use_ltr:
            recommendations = recommend_jobs_ltr(resume_text, skills)
        else:
            from modules.recommender import recommend_jobs
            recommendations = recommend_jobs(resume_text, skills)

        # 4. Explanations
        for rec in recommendations:
            rec["explanation"] = (
                f"Ranked via hybrid SBERT + LTR. "
                f"Top match: {rec['job_role']}."
            )

        return {
            "skills": skills,
            "score": score_result,
            "recommendations": recommendations,
            "features": score_result.get("features", {}),
        }


# Singleton
_pipeline = None


def get_pipeline(**kwargs) -> MLPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = MLPipeline(**kwargs)
    return _pipeline