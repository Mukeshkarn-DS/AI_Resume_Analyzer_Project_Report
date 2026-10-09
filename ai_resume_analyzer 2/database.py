"""
Database Models for AI Resume Analyzer
Uses Flask-SQLAlchemy with SQLite backend.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy instance (imported by app.py)
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship("Resume", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    file_path = db.Column(db.String(255))
    text_content = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    analyses = db.relationship("Analysis", backref="resume", lazy=True)

    def __repr__(self):
        return f"<Resume {self.id}>"


class Analysis(db.Model):
    __tablename__ = "analysis"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    score = db.Column(db.Float)
    breakdown = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Analysis score={self.score}>"