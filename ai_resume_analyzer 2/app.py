"""
AI Resume Analyzer and Career Guidance Portal
Main Flask Application with ML Pipeline Integration

Fixes applied:
- use_reloader=False to prevent watchdog crash during SBERT model loading
- Watchdog exclusion for site-packages and transformers cache
- SBERT pre-loaded at startup to avoid first-upload latency
- Robust error handling for DB, ML pipeline, and file uploads
"""

# ══════════════════════════════════════════════════════════
# WATCHDOG EXCLUSION — Must be set BEFORE importing anything
# ══════════════════════════════════════════════════════════
import os
os.environ["WATCHDOG_IGNORE_PATTERNS"] = "site-packages;transformers;.cache;__pycache__"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ══════════════════════════════════════════════════════════
# STANDARD IMPORTS
# ══════════════════════════════════════════════════════════
import mimetypes
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ══════════════════════════════════════════════════════════
# OPTIONAL DATABASE IMPORT
# ══════════════════════════════════════════════════════════
try:
    from database import db, User, Resume, Analysis
    DB_AVAILABLE = True
    print("[OK] database.py imported successfully.")
except ImportError as e:
    DB_AVAILABLE = False
    db = None
    User = Resume = Analysis = None
    print(f"[ERROR] Could not import database.py: {e}")

# ══════════════════════════════════════════════════════════
# EXISTING MODULES
# ══════════════════════════════════════════════════════════
from modules.resume_parser import extract_text
from modules.skill_extractor import extract_contact_info
from modules.career_guidance import get_career_guidance, get_overall_guidance

# ══════════════════════════════════════════════════════════
# OPTIONAL ML PIPELINE IMPORT
# ══════════════════════════════════════════════════════════
try:
    from ml_pipeline import get_pipeline
    ML_AVAILABLE = True
    print("[OK] ml_pipeline module imported successfully.")
except ImportError as e:
    ML_AVAILABLE = False
    get_pipeline = None
    print(f"[ERROR] ML pipeline failed to import: {e}")


# ══════════════════════════════════════════════════════════
# FLASK APP INITIALIZATION
# ══════════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me-please")

# Upload config
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ══════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ══════════════════════════════════════════════════════════
if DB_AVAILABLE:
    # Create folder FIRST (before SQLAlchemy tries to open the file)
    DB_DIR = os.path.join(os.getcwd(), "database")
    os.makedirs(DB_DIR, exist_ok=True)

    DB_PATH = os.path.join(DB_DIR, "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        print(f"[OK] Database initialized: {DB_PATH}")
    except Exception as e:
        print(f"[ERROR] Database init failed: {e}")
        DB_AVAILABLE = False
        db = None
        User = Resume = Analysis = None


# ══════════════════════════════════════════════════════════
# ML PIPELINE INITIALIZATION
# ══════════════════════════════════════════════════════════
pipeline = None
if ML_AVAILABLE:
    try:
        pipeline = get_pipeline(use_ml_scorer=True, use_ltr=True)
        print("[OK] ML pipeline initialized.")
    except Exception as e:
        print(f"[ERROR] ML pipeline failed to initialize: {e}")
        pipeline = None
else:
    print("[WARN] ML pipeline not available. Using rule-based fallback.")


# ══════════════════════════════════════════════════════════
# SBERT PRE-LOAD (prevents crash on first upload)
# ══════════════════════════════════════════════════════════
if pipeline is not None:
    try:
        print("[INFO] Pre-loading Sentence-BERT model (this may take a minute first time)...")
        from sentence_transformers import SentenceTransformer
        _ = SentenceTransformer("all-MiniLM-L6-v2")
        print("[OK] SBERT model loaded and cached.")
    except Exception as e:
        print(f"[WARN] Could not pre-load SBERT: {e}")
        print("[INFO] SBERT will be loaded on first upload instead.")


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def allowed_file(filename):
    """Check file extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_mime(file):
    """Check MIME type (defense-in-depth)."""
    mime = file.mimetype or mimetypes.guess_type(file.filename)[0]
    return mime in ALLOWED_MIMES


def login_required(f):
    """Session-based login decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def _grade(score):
    """Return (grade, color) for a given score."""
    if score >= 85:
        return "Excellent", "green"
    elif score >= 70:
        return "Good", "blue"
    elif score >= 50:
        return "Average", "orange"
    return "Needs Improvement", "red"


# ══════════════════════════════════════════════════════════
# ROUTES — PUBLIC
# ══════════════════════════════════════════════════════════
@app.route("/")
def index():
    """Home page — upload form."""
    return render_template("index.html")


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


# ══════════════════════════════════════════════════════════
# ROUTES — ANALYZE (core feature)
# ══════════════════════════════════════════════════════════
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Handle resume upload + analysis.
    Runs: parse -> contact -> ML pipeline -> guidance.
    """
    # ---- 1. Validate file presence ----
    if "resume" not in request.files:
        flash("No file uploaded.", "error")
        return redirect(url_for("index"))

    file = request.files["resume"]

    if not file or not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF and DOCX files are allowed.", "error")
        return redirect(url_for("index"))

    if not allowed_mime(file):
        flash("Invalid file type (MIME check failed).", "error")
        return redirect(url_for("index"))

    # ---- 2. Save file safely ----
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
    except Exception as e:
        flash(f"Could not save file: {e}", "error")
        return redirect(url_for("index"))

    # ---- 3. Parse resume text ----
    try:
        text = extract_text(filepath)
        if not text or len(text.strip()) < 20:
            flash("Could not extract meaningful text from resume.", "error")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Parsing error: {e}", "error")
        return redirect(url_for("index"))

    # ---- 4. Extract contact info ----
    try:
        contact = extract_contact_info(text)
    except Exception:
        contact = {
            "name": "Not found",
            "email": "Not found",
            "phone": "Not found",
            "linkedin": "Not found",
            "github": "Not found",
        }

    # ---- 5. Run ML pipeline or fallback ----
    try:
        if pipeline is not None:
            # === ML PATH ===
            ml_result = pipeline.run(text, contact)
            skills = ml_result["skills"]
            score_result = ml_result["score"]
            recommendations = ml_result["recommendations"]
            features = ml_result.get("features", {})
            score_value = score_result["score"]
            score_source = score_result["source"]
            breakdown = {}
            score_recommendations = []
        else:
            # === RULE-BASED FALLBACK ===
            from modules.skill_extractor import extract_skills
            from modules.scorer import calculate_resume_score
            from modules.recommender import recommend_jobs

            skills = extract_skills(text)
            legacy = calculate_resume_score(text, skills, contact)
            score_value = legacy["total"]
            score_source = "heuristic"
            breakdown = legacy["breakdown"]
            score_recommendations = legacy["recommendations"]
            recommendations = recommend_jobs(text, skills, top_n=5)
            features = {}
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Analysis error: {e}", "error")
        return redirect(url_for("index"))

    # ---- 6. Build score dict ----
    grade, grade_color = _grade(score_value)
    score_data = {
        "total": score_value,
        "source": score_source,
        "grade": grade,
        "grade_color": grade_color,
        "breakdown": breakdown,
        "recommendations": score_recommendations,
    }

    # ---- 7. Career guidance ----
    try:
        guidance = get_career_guidance(skills, recommendations)
    except Exception as e:
        print(f"[WARN] Career guidance error: {e}")
        guidance = []

    try:
        overall_advice = get_overall_guidance(skills, {"total": score_value})
    except Exception as e:
        print(f"[WARN] Overall advice error: {e}")
        overall_advice = []

    # ---- 8. Save to DB if logged in ----
    if DB_AVAILABLE and "user_id" in session:
        try:
            import json as _json
            resume_row = Resume(
                user_id=session["user_id"],
                file_path=filepath,
                text_content=text[:50000],
            )
            db.session.add(resume_row)
            db.session.commit()

            analysis_row = Analysis(
                resume_id=resume_row.id,
                score=score_value,
                breakdown=_json.dumps(breakdown),
            )
            db.session.add(analysis_row)
            db.session.commit()
        except Exception as e:
            print(f"[DB WARN] Could not save analysis: {e}")

    # ---- 9. Render ----
    return render_template(
        "result.html",
        contact=contact,
        skills=skills,
        score=score_data,
        recommendations=recommendations,
        guidance=guidance,
        overall_advice=overall_advice,
        features=features,
        filename=filename,
        word_count=len(text.split()),
        ml_enabled=(pipeline is not None),
    )


# ══════════════════════════════════════════════════════════
# ROUTES — AUTH
# ══════════════════════════════════════════════════════════
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not DB_AVAILABLE:
        flash("Database not configured. Signup unavailable.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("signup"))

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        session["user_name"] = user.name
        flash("Account created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if not DB_AVAILABLE:
        flash("Database not configured. Login unavailable.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.name
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════
# ROUTES — DASHBOARD
# ══════════════════════════════════════════════════════════
@app.route("/dashboard")
@login_required
def dashboard():
    if not DB_AVAILABLE:
        flash("Dashboard requires database.", "error")
        return redirect(url_for("index"))

    user_id = session["user_id"]
    resumes = (
        Resume.query
        .filter_by(user_id=user_id)
        .order_by(Resume.upload_date.desc())
        .limit(20)
        .all()
    )

    history = []
    for r in resumes:
        latest = (
            Analysis.query
            .filter_by(resume_id=r.id)
            .order_by(Analysis.timestamp.desc())
            .first()
        )
        history.append({
            "resume_id": r.id,
            "file_path": r.file_path,
            "upload_date": r.upload_date,
            "score": latest.score if latest else None,
            "timestamp": latest.timestamp if latest else None,
        })

    return render_template(
        "dashboard.html",
        history=history,
        user_name=session.get("user_name"),
    )


# ══════════════════════════════════════════════════════════
# ROUTES — API (JSON)
# ══════════════════════════════════════════════════════════
@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "ml_enabled": pipeline is not None,
        "db_enabled": DB_AVAILABLE,
    })


# ══════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════
@app.errorhandler(413)
def too_large(e):
    flash("File is too large. Maximum size is 5 MB.", "error")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    flash("Something went wrong. Please try again.", "error")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"

    print("=" * 60)
    print("AI Resume Analyzer & Career Guidance Portal")
    print(f"  ML Pipeline : {'ENABLED' if pipeline else 'DISABLED (heuristic fallback)'}")
    print(f"  Database    : {'ENABLED' if DB_AVAILABLE else 'DISABLED'}")
    print(f"  Debug mode  : {debug_mode}")
    print("=" * 60)

    # ✅ KEY FIX: use_reloader=False prevents watchdog crash during SBERT loading
    app.run(
        debug=debug_mode,
        use_reloader=False,
        host="0.0.0.0",
        port=5000,
    )