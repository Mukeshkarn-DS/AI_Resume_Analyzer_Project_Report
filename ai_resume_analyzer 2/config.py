import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SQLALCHEMY_DATABASE_URI = "sqlite:///database/app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SBERT_MODEL_NAME = "all-MiniLM-L6-v2"
    NER_MODEL_PATH = os.path.join("models", "ner_skill")
    RESUME_SCORER_PATH = os.path.join("models", "resume_scorer.pkl")
    XGB_RANKER_PATH = os.path.join("models", "xgb_ranker.json")